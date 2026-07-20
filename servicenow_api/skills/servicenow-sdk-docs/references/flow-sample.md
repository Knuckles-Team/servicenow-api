# Flow Sample

This is a sample of using the various `Flow` APIs available in the ServiceNow SDK

## Example Location
Source Code: [assets/samples/flow-sample](../assets/samples/flow-sample)

## Code Samples

### `flow-trigger-inbound-email.now.ts`
Path: [flow-sample/fluent/flow-trigger-inbound-email.now.ts](../assets/samples/flow-sample/fluent/flow-trigger-inbound-email.now.ts)

```typescript
import { action, Flow, wfa, trigger } from '@servicenow/sdk/automation'

export const emailIncidentTaskFlow = Flow(
    {
        $id: Now.ID['email_incident_task_flow'],
        name: 'Email Incident/Task Creation Flow',
        description: 'Creates incidents or tasks based on email content with "raise incident or task" in subject',
    },
    wfa.trigger(
        trigger.application.inboundEmail,
        { $id: Now.ID['inbound_email_trigger'] },
        {
            email_conditions: 'subjectLIKEraise incident or task',
            target_table: 'incident',
        }
    ),
    (params) => {
        wfa.action(
            action.core.log,
            { $id: Now.ID['log_email_received'] },
            {
                log_level: 'info',
                log_message: `Email received from: ${wfa.dataPill(params.trigger.from_address, 'string')}, Subject: ${wfa.dataPill(params.trigger.subject, 'string')}`,
            }
        )

        const sender = wfa.action(
            action.core.lookUpRecord,
            { $id: Now.ID['lookup_sender'] },
            {
                table: 'sys_user',
                conditions: `email=${wfa.dataPill(params.trigger.from_address, 'string')}`,
                sort_type: 'sort_asc',
                if_multiple_records_are_found_action: 'use_first_record',
            }
        )

        // Internal P1 path — two tasks
        wfa.flowLogic.if(
            {
                $id: Now.ID['check_internal_p1'],
                condition: `${wfa.dataPill(sender.Record.email, 'string')}LIKEservicenow^${wfa.dataPill(params.trigger.subject, 'string')}LIKEP1`,
                annotation: 'Internal sender with P1 subject',
            },
            () => {
                const senderManager = wfa.action(
                    action.core.lookUpRecord,
                    { $id: Now.ID['lookup_sender_manager'] },
                    {
                        table: 'sys_user',
                        conditions: `sys_id=${wfa.dataPill(sender.Record.manager, 'reference')}`,
                        sort_type: 'sort_asc',
                        if_multiple_records_are_found_action: 'use_first_record',
                    }
                )

                wfa.action(
                    action.core.createTask,
                    { $id: Now.ID['task_for_manager'] },
                    {
                        task_table: 'incident',
                        field_values: TemplateValue({
                            priority: 1,
                            assigned_to: wfa.dataPill(senderManager.Record.sys_id, 'reference'),
                            short_description: wfa.dataPill(params.trigger.inbound_email.body, 'reference'),
                            urgency: 1,
                            impact: 1,
                        }),
                    }
                )

                wfa.action(
                    action.core.createTask,
                    { $id: Now.ID['task_for_sender'] },
                    {
                        task_table: 'incident',
                        field_values: TemplateValue({
                            priority: 1,
                            assigned_to: wfa.dataPill(sender.Record.sys_id, 'reference'),
                            short_description: wfa.dataPill(params.trigger.subject, 'string'),
                            urgency: 1,
                            impact: 1,
                        }),
                    }
                )
            }
        )

        // External / non-P1 path — P3 incident + copy attachments
        wfa.flowLogic.else({ $id: Now.ID['create_p3_incident_branch'] }, () => {
            const p3Incident = wfa.action(
                action.core.createRecord,
                { $id: Now.ID['create_p3_incident'] },
                {
                    table_name: 'incident',
                    values: TemplateValue({
                        priority: 4,
                        short_description: wfa.dataPill(params.trigger.subject, 'string'),
                        description: `From: ${wfa.dataPill(params.trigger.from_address, 'string')}\n\n${wfa.dataPill(params.trigger.inbound_email.body, 'reference')}`,
                        contact_type: 'email',
                        caller_id: wfa.dataPill(sender.Record.sys_id, 'reference'),
                    }),
                }
            )

            const attachments = wfa.action(
                action.core.getAttachmentsOnRecord,
                { $id: Now.ID['get_email_attachments'] },
                { source_record: wfa.dataPill(params.trigger.inbound_email.sys_id, 'reference') }
            )

            wfa.flowLogic.forEach(
                wfa.dataPill(attachments.parameter, 'records'),
                { $id: Now.ID['copy_attachments_loop'] },
                () => {
                    wfa.action(
                        action.core.copyAttachment,
                        { $id: Now.ID['copy_attachment'] },
                        {
                            target_record: wfa.dataPill(p3Incident.record, 'reference'),
                            attachment_record: wfa.dataPill(attachments.parameter, 'records'),
                            table: 'incident',
                        }
                    )
                }
            )

            wfa.action(
                action.core.sendEmail,
                { $id: Now.ID['confirm_p3_email'] },
                {
                    table_name: 'incident',
                    ah_to: wfa.dataPill(params.trigger.from_address, 'string'),
                    ah_subject: `Incident Created: ${wfa.dataPill(params.trigger.subject, 'string')}`,
                    ah_body: `Your request has been received and a P3 incident has been created. Our team will be in touch shortly.`,
                    record: wfa.dataPill(p3Incident.record, 'reference'),
                }
            )
        })
    }
)

```

### `flow-trigger-record.now.ts`
Path: [flow-sample/fluent/flow-trigger-record.now.ts](../assets/samples/flow-sample/fluent/flow-trigger-record.now.ts)

```typescript
import { action, Flow, wfa, trigger } from '@servicenow/sdk/automation'

// ── trigger.record.created ────────────────────────────────────────────────────

export const incidentSeverityAlertFlow = Flow(
    {
        $id: Now.ID['incident_severity_alert_flow'],
        name: 'Incident Severity Alert Flow',
        description: 'Alerts managers and team members based on incident severity for incidents with empty origin',
    },
    wfa.trigger(
        trigger.record.created,
        { $id: Now.ID['empty_origin_incident_trigger'] },
        {
            table: 'incident',
            condition: 'origin=NULL',
            run_flow_in: 'background',
            run_on_extended: 'false',
            run_when_setting: 'both',
            run_when_user_setting: 'any',
            run_when_user_list: [],
        }
    ),
    (params) => {
        wfa.action(
            action.core.log,
            { $id: Now.ID['log_incident_short_description'] },
            {
                log_level: 'info',
                log_message: `Incident created: ${wfa.dataPill(params.trigger.current.short_description, 'string')}`,
            }
        )

        wfa.flowLogic.if(
            {
                $id: Now.ID['check_severity_high'],
                condition: `${wfa.dataPill(params.trigger.current.severity, 'string')}=1`,
                annotation: 'High severity (1)',
            },
            () => {
                const assignmentGroup = wfa.action(
                    action.core.lookUpRecord,
                    { $id: Now.ID['lookup_assignment_group'] },
                    {
                        table: 'sys_user_group',
                        conditions: `sys_id=${wfa.dataPill(params.trigger.current.assignment_group, 'reference')}`,
                        sort_type: 'sort_asc',
                        if_multiple_records_are_found_action: 'use_first_record',
                    }
                )

                const manager = wfa.action(
                    action.core.lookUpRecord,
                    { $id: Now.ID['lookup_manager_details'] },
                    {
                        table: 'sys_user',
                        conditions: `sys_id=${wfa.dataPill(assignmentGroup.Record.manager, 'reference')}`,
                        sort_type: 'sort_asc',
                        if_multiple_records_are_found_action: 'use_first_record',
                    }
                )

                wfa.action(
                    action.core.sendNotification,
                    { $id: Now.ID['send_urgent_email_to_manager'] },
                    {
                        table_name: 'incident',
                        record: wfa.dataPill(params.trigger.current.sys_id, 'reference'),
                        notification: 'high_severity_incident_manager_notification',
                    }
                )

                wfa.flowLogic.forEach(
                    wfa.dataPill(params.trigger.current.additional_assignee_list, 'array.string'),
                    { $id: Now.ID['foreach_additional_assignees_high'] },
                    () => {
                        const assignee = wfa.action(
                            action.core.lookUpRecord,
                            { $id: Now.ID['lookup_assignee_details_high'] },
                            {
                                table: 'sys_user',
                                conditions: `sys_id=${wfa.dataPill(params.trigger.current.additional_assignee_list, 'array.string')}`,
                                sort_type: 'sort_asc',
                                if_multiple_records_are_found_action: 'use_first_record',
                            }
                        )

                        wfa.action(
                            action.core.sendSms,
                            { $id: Now.ID['send_sms_to_assignee_high'] },
                            {
                                recipients: `${wfa.dataPill(assignee.Record.phone, 'string')}`,
                                message: `High severity incident: ${wfa.dataPill(params.trigger.current.short_description, 'string')}`,
                            }
                        )
                    }
                )

                wfa.action(
                    action.core.updateRecord,
                    { $id: Now.ID['update_work_notes_high'] },
                    {
                        table_name: 'incident',
                        record: wfa.dataPill(params.trigger.current.sys_id, 'reference'),
                        values: TemplateValue({
                            work_notes: `Manager ${wfa.dataPill(manager.Record.name, 'string')} notified via email and team notified via SMS.`,
                        }),
                    }
                )
            }
        )

        wfa.flowLogic.elseIf(
            {
                $id: Now.ID['check_severity_medium'],
                condition: `${wfa.dataPill(params.trigger.current.severity, 'string')}=2`,
                annotation: 'Medium severity (2)',
            },
            () => {
                wfa.flowLogic.forEach(
                    wfa.dataPill(params.trigger.current.additional_assignee_list, 'array.string'),
                    { $id: Now.ID['foreach_additional_assignees_medium'] },
                    () => {
                        const assignee = wfa.action(
                            action.core.lookUpRecord,
                            { $id: Now.ID['lookup_assignee_details_medium'] },
                            {
                                table: 'sys_user',
                                conditions: `sys_id=${wfa.dataPill(params.trigger.current.additional_assignee_list, 'array.string')}`,
                                sort_type: 'sort_asc',
                                if_multiple_records_are_found_action: 'use_first_record',
                            }
                        )

                        wfa.action(
                            action.core.sendSms,
                            { $id: Now.ID['send_sms_to_assignee_medium'] },
                            {
                                recipients: `${wfa.dataPill(assignee.Record.phone, 'string')}`,
                                message: `Medium severity incident: ${wfa.dataPill(params.trigger.current.short_description, 'string')}`,
                            }
                        )
                    }
                )
            }
        )

        wfa.action(
            action.core.updateRecord,
            { $id: Now.ID['update_incident_to_in_progress'] },
            {
                table_name: 'incident',
                record: wfa.dataPill(params.trigger.current.sys_id, 'reference'),
                values: TemplateValue({ state: '2' }),
            }
        )
    }
)

// ── trigger.record.updated ────────────────────────────────────────────────────

export const changeRequestApprovalNotificationFlow = Flow(
    {
        $id: Now.ID['change_request_approval_notification_flow'],
        name: 'Change Request Approval Notification Flow',
        description: 'Sends formatted notification to requester when change request is approved',
    },
    wfa.trigger(
        trigger.record.updated,
        { $id: Now.ID['change_request_approved_trigger'] },
        {
            table: 'change_request',
            condition: 'approval=approved',
            run_flow_in: 'background',
            trigger_strategy: 'unique_changes',
            run_when_user_list: [],
            run_when_setting: 'both',
            run_on_extended: 'false',
            run_when_user_setting: 'any',
        }
    ),
    (params) => {
        const requester = wfa.action(
            action.core.lookUpRecord,
            { $id: Now.ID['lookup_requester_details'] },
            {
                table: 'sys_user',
                conditions: `sys_id=${wfa.dataPill(params.trigger.current.requested_by, 'reference')}`,
                sort_type: 'sort_asc',
                if_multiple_records_are_found_action: 'use_first_record',
            }
        )

        wfa.action(
            action.core.sendEmail,
            { $id: Now.ID['send_approval_notification_email'] },
            {
                table_name: 'change_request',
                watermark_email: true,
                ah_subject: `Change Request ${wfa.dataPill(params.trigger.current.number, 'string')} - Approved`,
                ah_body: `Your change request has been approved.`,
                record: wfa.dataPill(params.trigger.current.sys_id, 'reference'),
                ah_to: wfa.dataPill(requester.Record.email, 'string'),
            }
        )

        wfa.action(
            action.core.updateRecord,
            { $id: Now.ID['update_work_notes_notification_sent'] },
            {
                table_name: 'change_request',
                record: wfa.dataPill(params.trigger.current.sys_id, 'reference'),
                values: TemplateValue({
                    work_notes: `Approval notification sent to ${wfa.dataPill(requester.Record.name, 'string')} (${wfa.dataPill(requester.Record.email, 'string')})`,
                }),
            }
        )
    }
)

// ── trigger.record.createdOrUpdated ──────────────────────────────────────────

export const changeRiskTaggingFlow = Flow(
    {
        $id: Now.ID['change_risk_tagging_flow'],
        name: 'Change Risk Tagging Flow',
        description: 'Tags change requests with high-risk label when created or updated with high impact',
    },
    wfa.trigger(
        trigger.record.createdOrUpdated,
        { $id: Now.ID['change_risk_trigger'] },
        {
            table: 'change_request',
            condition: 'active=true^impact=1',
            run_flow_in: 'background',
            run_on_extended: 'false',
            run_when_setting: 'both',
            run_when_user_setting: 'any',
            run_when_user_list: [],
        }
    ),
    (params) => {
        wfa.action(
            action.core.updateRecord,
            { $id: Now.ID['tag_high_risk'] },
            {
                table_name: 'change_request',
                record: wfa.dataPill(params.trigger.current.sys_id, 'reference'),
                values: TemplateValue({
                    risk: 'high',
                    work_notes: 'Automatically tagged as high-risk due to high impact.',
                }),
            }
        )

        const cab = wfa.action(
            action.core.lookUpRecord,
            { $id: Now.ID['lookup_cab_group'] },
            {
                table: 'sys_user_group',
                conditions: 'name=CAB^active=true',
                sort_type: 'sort_asc',
                if_multiple_records_are_found_action: 'use_first_record',
            }
        )

        wfa.action(
            action.core.sendNotification,
            { $id: Now.ID['notify_cab_high_risk'] },
            {
                table_name: 'change_request',
                record: wfa.dataPill(params.trigger.current.sys_id, 'reference'),
                notification: 'high_risk_change_cab_notification',
            }
        )

        wfa.action(
            action.core.log,
            { $id: Now.ID['log_risk_tagged'] },
            {
                log_level: 'warn',
                log_message: `Change ${wfa.dataPill(params.trigger.current.number, 'string')} tagged as high-risk. CAB group ${wfa.dataPill(cab.Record.name, 'string')} notified.`,
            }
        )
    }
)

```

### `subflow-sample.now.ts`
Path: [flow-sample/fluent/subflow-sample.now.ts](../assets/samples/flow-sample/fluent/subflow-sample.now.ts)

```typescript
import { Subflow, action, wfa } from '@servicenow/sdk/automation'
import { BooleanColumn, ReferenceColumn, StringColumn } from '@servicenow/sdk/core'

export const newUserOnboardingSubflow = Subflow(
    {
        $id: Now.ID['new_user_onboarding_subflow'],
        name: 'New User Onboarding Subflow',
        description: 'Sends welcome notification, assigns laptop and desk, returns assignment results',
        inputs: {
            user_sys_id: ReferenceColumn({
                label: 'User',
                referenceTable: 'sys_user',
                mandatory: true,
            }),
            office_location: ReferenceColumn({
                label: 'Office Location',
                referenceTable: 'cmn_location',
                mandatory: true,
            }),
        },
        outputs: {
            laptop_assigned: BooleanColumn({ label: 'Laptop Assigned' }),
            desk_assigned: BooleanColumn({ label: 'Desk Assigned' }),
            laptop_number: StringColumn({ label: 'Laptop Asset Number', maxLength: 40 }),
            desk_number: StringColumn({ label: 'Desk Asset Number', maxLength: 40 }),
        },
        flowVariables: {
            laptop_found: BooleanColumn({ label: 'Laptop Found Flag', default: false }),
            desk_found: BooleanColumn({ label: 'Desk Found Flag', default: false }),
        },
    },
    (params) => {
        const user = wfa.action(
            action.core.lookUpRecord,
            { $id: Now.ID['lookup_user'] },
            {
                table: 'sys_user',
                conditions: `sys_id=${wfa.dataPill(params.inputs.user_sys_id, 'reference')}`,
                sort_type: 'sort_asc',
                if_multiple_records_are_found_action: 'use_first_record',
            }
        )

        wfa.action(
            action.core.sendNotification,
            { $id: Now.ID['send_welcome_notification'] },
            {
                table_name: 'sys_user',
                record: wfa.dataPill(params.inputs.user_sys_id, 'reference'),
                notification: 'new_user_welcome_notification',
            }
        )

        const availableLaptop = wfa.action(
            action.core.lookUpRecord,
            { $id: Now.ID['lookup_available_laptop'] },
            {
                table: 'alm_hardware',
                conditions: 'assigned_to=NULL^install_status=1^substatus=available',
                sort_type: 'sort_asc',
                if_multiple_records_are_found_action: 'use_first_record',
            }
        )

        wfa.flowLogic.if(
            {
                $id: Now.ID['check_laptop_available'],
                condition: `${wfa.dataPill(availableLaptop.Record.sys_id, 'reference')}!=NULL`,
                annotation: 'Available laptop found',
            },
            () => {
                wfa.action(
                    action.core.updateRecord,
                    { $id: Now.ID['assign_laptop'] },
                    {
                        table_name: 'alm_hardware',
                        record: wfa.dataPill(availableLaptop.Record.sys_id, 'reference'),
                        values: TemplateValue({
                            assigned_to: wfa.dataPill(params.inputs.user_sys_id, 'reference'),
                            install_status: '2',
                            substatus: 'in_use',
                        }),
                    }
                )
            }
        )

        wfa.flowLogic.else(
            { $id: Now.ID['no_laptop_available'] },
            () => {
                wfa.action(
                    action.core.log,
                    { $id: Now.ID['log_no_laptop'] },
                    {
                        log_level: 'warn',
                        log_message: `No available laptop found for ${wfa.dataPill(user.Record.name, 'string')} — manual assignment required.`,
                    }
                )
            }
        )

        const availableDesk = wfa.action(
            action.core.lookUpRecord,
            { $id: Now.ID['lookup_available_desk'] },
            {
                table: 'alm_asset',
                conditions: `assigned_to=NULL^location=${wfa.dataPill(params.inputs.office_location, 'reference')}^install_status=1^substatus=available`,
                sort_type: 'sort_asc',
                if_multiple_records_are_found_action: 'use_first_record',
            }
        )

        wfa.flowLogic.if(
            {
                $id: Now.ID['check_desk_available'],
                condition: `${wfa.dataPill(availableDesk.Record.sys_id, 'reference')}!=NULL`,
                annotation: 'Available desk found at office location',
            },
            () => {
                wfa.action(
                    action.core.updateRecord,
                    { $id: Now.ID['assign_desk'] },
                    {
                        table_name: 'alm_asset',
                        record: wfa.dataPill(availableDesk.Record.sys_id, 'reference'),
                        values: TemplateValue({
                            assigned_to: wfa.dataPill(params.inputs.user_sys_id, 'reference'),
                            install_status: '2',
                            substatus: 'in_use',
                        }),
                    }
                )
            }
        )

        wfa.flowLogic.else(
            { $id: Now.ID['no_desk_available'] },
            () => {
                wfa.action(
                    action.core.log,
                    { $id: Now.ID['log_no_desk'] },
                    {
                        log_level: 'warn',
                        log_message: `No available desk at office location for ${wfa.dataPill(user.Record.name, 'string')} — manual assignment required.`,
                    }
                )
            }
        )

        wfa.action(
            action.core.sendNotification,
            { $id: Now.ID['send_onboarding_complete'] },
            {
                table_name: 'sys_user',
                record: wfa.dataPill(params.inputs.user_sys_id, 'reference'),
                notification: 'user_onboarding_complete_notification',
            }
        )

        wfa.flowLogic.assignSubflowOutputs(
            {
                $id: Now.ID['assign_outputs'],
                annotation: 'Return laptop and desk assignment results',
            },
            params.outputs,
            {
                laptop_assigned: true,
                desk_assigned: true,
                laptop_number: wfa.dataPill(availableLaptop.Record.asset_tag, 'string'),
                desk_number: wfa.dataPill(availableDesk.Record.asset_tag, 'string'),
            }
        )
    }
)

```

### `flow-trigger-sla-task.now.ts`
Path: [flow-sample/fluent/flow-trigger-sla-task.now.ts](../assets/samples/flow-sample/fluent/flow-trigger-sla-task.now.ts)

```typescript
import { action, Flow, wfa, trigger } from '@servicenow/sdk/automation'

export const slaTaskEscalationFlow = Flow(
    {
        $id: Now.ID['sla_task_escalation_flow'],
        name: 'SLA Task Escalation Flow',
        description: 'Escalates tasks at 75% and 90% SLA milestones and confirms resolution',
    },
    wfa.trigger(
        trigger.application.slaTask,
        { $id: Now.ID['sla_task_trigger'] },
        {}
    ),
    (params) => {
        // ── 75% milestone ────────────────────────────────────────────────────────
        wfa.action(
            action.core.slaPercentageTimer,
            { $id: Now.ID['wait_75_percent'], annotation: 'Pause until 75% of SLA time elapsed' },
            { percentage: 75 }
        )

        const slat75 = wfa.action(
            action.core.lookUpRecord,
            { $id: Now.ID['lookup_sla_75'] },
            {
                table: 'task_sla',
                conditions: `sys_id=${wfa.dataPill(params.trigger.task_sla_record, 'reference')}`,
                sort_type: 'sort_asc',
                if_multiple_records_are_found_action: 'use_first_record',
            }
        )

        const task75 = wfa.action(
            action.core.lookUpRecord,
            { $id: Now.ID['lookup_task_75'] },
            {
                table: 'task',
                conditions: `sys_id=${wfa.dataPill(slat75.Record.task, 'reference')}`,
                sort_type: 'sort_asc',
                if_multiple_records_are_found_action: 'use_first_record',
            }
        )

        wfa.flowLogic.if(
            {
                $id: Now.ID['check_not_assigned_75'],
                condition: `${wfa.dataPill(task75.Record.assigned_to, 'reference')}=NULL`,
                annotation: 'Task is unassigned at 75%',
            },
            () => {
                wfa.action(
                    action.core.updateRecord,
                    { $id: Now.ID['worknote_unassigned_75'] },
                    {
                        table_name: 'task',
                        record: wfa.dataPill(task75.Record.sys_id, 'reference'),
                        values: TemplateValue({ work_notes: 'Warning: task is unassigned at 75% of SLA time.' }),
                    }
                )
            }
        )

        wfa.flowLogic.else(
            { $id: Now.ID['handle_assigned_75'] },
            () => {
                wfa.action(
                    action.core.updateRecord,
                    { $id: Now.ID['worknote_assigned_75'] },
                    {
                        table_name: 'task',
                        record: wfa.dataPill(task75.Record.sys_id, 'reference'),
                        values: TemplateValue({ work_notes: 'SLA at 75% — manager notified.' }),
                    }
                )

                wfa.action(
                    action.core.sendNotification,
                    { $id: Now.ID['notify_manager_75'] },
                    {
                        table_name: 'task',
                        record: wfa.dataPill(task75.Record.sys_id, 'reference'),
                        notification: 'sla_escalation_level_1_notification',
                    }
                )
            }
        )

        // ── 90% milestone ────────────────────────────────────────────────────────
        wfa.action(
            action.core.slaPercentageTimer,
            { $id: Now.ID['wait_90_percent'], annotation: 'Pause until 90% of SLA time elapsed' },
            { percentage: 90 }
        )

        const slat90 = wfa.action(
            action.core.lookUpRecord,
            { $id: Now.ID['lookup_sla_90'] },
            {
                table: 'task_sla',
                conditions: `sys_id=${wfa.dataPill(params.trigger.task_sla_record, 'reference')}`,
                sort_type: 'sort_asc',
                if_multiple_records_are_found_action: 'use_first_record',
            }
        )

        const task90 = wfa.action(
            action.core.lookUpRecord,
            { $id: Now.ID['lookup_task_90'] },
            {
                table: 'task',
                conditions: `sys_id=${wfa.dataPill(slat90.Record.task, 'reference')}`,
                sort_type: 'sort_asc',
                if_multiple_records_are_found_action: 'use_first_record',
            }
        )

        wfa.flowLogic.if(
            {
                $id: Now.ID['check_resolved_90'],
                condition: `${wfa.dataPill(task90.Record.state, 'string')}=6`,
                annotation: 'Task already resolved at 90%',
            },
            () => {
                wfa.action(
                    action.core.updateRecord,
                    { $id: Now.ID['worknote_resolved_90'] },
                    {
                        table_name: 'task',
                        record: wfa.dataPill(task90.Record.sys_id, 'reference'),
                        values: TemplateValue({ work_notes: 'Task resolved before 90% SLA milestone — no escalation needed.' }),
                    }
                )
            }
        )

        wfa.flowLogic.else(
            { $id: Now.ID['handle_unresolved_90'] },
            () => {
                wfa.action(
                    action.core.sendNotification,
                    { $id: Now.ID['urgent_escalation_90'] },
                    {
                        table_name: 'task',
                        record: wfa.dataPill(task90.Record.sys_id, 'reference'),
                        notification: 'sla_escalation_urgent_notification',
                    }
                )

                wfa.action(
                    action.core.waitForCondition,
                    { $id: Now.ID['wait_for_resolution'] },
                    {
                        table_name: 'task',
                        record: wfa.dataPill(task90.Record.sys_id, 'reference'),
                        conditions: 'state=6',
                        timeout_duration: Duration({ days: 7 }),
                    }
                )

                wfa.action(
                    action.core.sendNotification,
                    { $id: Now.ID['confirm_resolution'] },
                    {
                        table_name: 'task',
                        record: wfa.dataPill(task90.Record.sys_id, 'reference'),
                        notification: 'sla_resolution_confirmation_notification',
                    }
                )
            }
        )
    }
)

```

### `flow-trigger-remote-table-query.now.ts`
Path: [flow-sample/fluent/flow-trigger-remote-table-query.now.ts](../assets/samples/flow-sample/fluent/flow-trigger-remote-table-query.now.ts)

```typescript
import { action, Flow, wfa, trigger } from '@servicenow/sdk/automation'

export const remoteUserQueryFlow = Flow(
    {
        $id: Now.ID['remote_user_query_flow'],
        name: 'Remote User Query Enrichment Flow',
        description: 'Enriches user records returned to remote systems with active incident counts',
    },
    wfa.trigger(trigger.application.remoteTableQuery, { $id: Now.ID['remote_query_trigger'] }, {}),
    (params) => {
        wfa.action(
            action.core.log,
            { $id: Now.ID['log_remote_query'] },
            {
                log_level: 'info',
                log_message: `Remote query received - Query ID: ${wfa.dataPill(params.trigger.query_id, 'string')}, Parameters: ${wfa.dataPill(params.trigger.query_parameters, 'string')}, Table: ${wfa.dataPill(params.trigger.table_name, 'string')}}`,
            }
        )

        wfa.flowLogic.if(
            {
                $id: Now.ID['check_user_table'],
                condition: `${wfa.dataPill(params.trigger.table_name, 'table_name')}=sys_user`,
                annotation: 'Query is for sys_user table',
            },
            () => {
                const activeUsers = wfa.action(
                    action.core.lookUpRecords,
                    { $id: Now.ID['lookup_active_users'] },
                    {
                        table: 'sys_user',
                        conditions: 'active=true^departmentISNOTEMPTY',
                        max_results: 500,
                        sort_column: 'name',
                        sort_type: 'sort_asc',
                    }
                )

                wfa.flowLogic.forEach(
                    wfa.dataPill(activeUsers.Records, 'records'),
                    { $id: Now.ID['foreach_users'] },
                    () => {
                        const userIncidents = wfa.action(
                            action.core.lookUpRecords,
                            { $id: Now.ID['lookup_user_incidents'] },
                            {
                                table: 'incident',
                                conditions: `assigned_to=${wfa.dataPill(activeUsers.Records, 'records')}^active=true`,
                                max_results: 100,
                                sort_column: 'priority',
                                sort_type: 'sort_asc',
                            }
                        )

                        wfa.action(
                            action.core.log,
                            { $id: Now.ID['log_user_incident_count'] },
                            {
                                log_level: 'info',
                                log_message: `User enrichment complete — incidents: ${wfa.dataPill(userIncidents.Records, 'records')}`,
                            }
                        )
                    }
                )
            }
        )

        wfa.flowLogic.else({ $id: Now.ID['unhandled_table_branch'] }, () => {
            wfa.action(
                action.core.log,
                { $id: Now.ID['log_unhandled_table'] },
                {
                    log_level: 'warn',
                    log_message: `Remote query for unhandled table: ${wfa.dataPill(params.trigger.table_name, 'table_name')} — no enrichment applied.`,
                }
            )
        })
    }
)

```

### `flow-trigger-knowledge-management.now.ts`
Path: [flow-sample/fluent/flow-trigger-knowledge-management.now.ts](../assets/samples/flow-sample/fluent/flow-trigger-knowledge-management.now.ts)

```typescript
import { action, Flow, wfa, trigger } from '@servicenow/sdk/automation'

export const knowledgeArticleQaFlow = Flow(
    {
        $id: Now.ID['knowledge_article_qa_flow'],
        name: 'Knowledge Article QA Flow',
        description: 'Validates published knowledge articles and notifies authors or managers based on quality',
    },
    wfa.trigger(
        trigger.application.knowledgeManagement,
        { $id: Now.ID['knowledge_management_trigger'] },
        {}
    ),
    (params) => {
        const article = wfa.action(
            action.core.lookUpRecord,
            { $id: Now.ID['lookup_kb_article'] },
            {
                table: 'kb_knowledge',
                conditions: `sys_id=${wfa.dataPill(params.trigger.knowledge, 'reference')}`,
                sort_type: 'sort_asc',
                if_multiple_records_are_found_action: 'use_first_record',
            }
        )

        const author = wfa.action(
            action.core.lookUpRecord,
            { $id: Now.ID['lookup_author'] },
            {
                table: 'sys_user',
                conditions: `sys_id=${wfa.dataPill(article.Record.author, 'reference')}`,
                sort_type: 'sort_asc',
                if_multiple_records_are_found_action: 'use_first_record',
            }
        )

        // QA check 1: article must have content
        wfa.flowLogic.if(
            {
                $id: Now.ID['check_content_empty'],
                condition: `${wfa.dataPill(article.Record.text, 'string')}ISEMPTY`,
                annotation: 'Article body is empty',
            },
            () => {
                wfa.action(
                    action.core.updateRecord,
                    { $id: Now.ID['revert_to_draft_no_content'] },
                    {
                        table_name: 'kb_knowledge',
                        record: wfa.dataPill(article.Record.sys_id, 'reference'),
                        values: TemplateValue({
                            workflow_state: 'draft',
                            comments: 'QA failed: article body is empty. Please add content before re-publishing.',
                        }),
                    }
                )

                const revisionTask = wfa.action(
                    action.core.createRecord,
                    { $id: Now.ID['create_content_task'] },
                    {
                        table_name: 'task',
                        values: TemplateValue({
                            short_description: `Add content to KB article: ${wfa.dataPill(article.Record.short_description, 'string')}`,
                            assigned_to: wfa.dataPill(author.Record.sys_id, 'reference'),
                            priority: 3,
                            state: 1,
                        }),
                    }
                )

                wfa.action(
                    action.core.sendNotification,
                    { $id: Now.ID['notify_author_no_content'] },
                    {
                        record: wfa.dataPill(revisionTask.record, 'reference'),
                        notification: 'kb_article_revision_needed',
                    }
                )

                wfa.flowLogic.endFlow({
                    $id: Now.ID['end_flow_no_content'],
                    annotation: 'End — article failed QA (no content)',
                })
            }
        )

        // QA check 2: article must have a title
        wfa.flowLogic.if(
            {
                $id: Now.ID['check_title_empty'],
                condition: `${wfa.dataPill(article.Record.short_description, 'string')}ISEMPTY`,
                annotation: 'Article title is missing',
            },
            () => {
                wfa.action(
                    action.core.updateRecord,
                    { $id: Now.ID['revert_to_draft_no_title'] },
                    {
                        table_name: 'kb_knowledge',
                        record: wfa.dataPill(article.Record.sys_id, 'reference'),
                        values: TemplateValue({
                            workflow_state: 'draft',
                            comments: 'QA failed: article title is missing.',
                        }),
                    }
                )

                wfa.flowLogic.endFlow({
                    $id: Now.ID['end_flow_no_title'],
                    annotation: 'End — article failed QA (no title)',
                })
            }
        )

        // Article passed QA — stamp approval comment
        wfa.action(
            action.core.updateRecord,
            { $id: Now.ID['mark_qa_approved'] },
            {
                table_name: 'kb_knowledge',
                record: wfa.dataPill(article.Record.sys_id, 'reference'),
                values: TemplateValue({
                    comments: `QA approved on ${wfa.dataPill(params.trigger.run_start_date_time, 'glide_date_time')}.`,
                }),
            }
        )

        const attachments = wfa.action(
            action.core.getAttachmentsOnRecord,
            { $id: Now.ID['get_article_attachments'] },
            { source_record: wfa.dataPill(article.Record.sys_id, 'reference') }
        )

        // Notify knowledge manager if article has attachments (high quality)
        wfa.flowLogic.if(
            {
                $id: Now.ID['check_has_attachments'],
                condition: `${wfa.dataPill(attachments.parameter, 'array.string')}ISNOTEMPTY`,
                annotation: 'Article has supporting attachments — high quality',
            },
            () => {
                const kbManager = wfa.action(
                    action.core.lookUpRecord,
                    { $id: Now.ID['lookup_kb_manager'] },
                    {
                        table: 'sys_user',
                        conditions: 'roles=knowledge_manager^active=true',
                        sort_type: 'sort_asc',
                        if_multiple_records_are_found_action: 'use_first_record',
                    }
                )

                wfa.action(
                    action.core.createRecord,
                    { $id: Now.ID['create_feature_task'] },
                    {
                        table_name: 'task',
                        values: TemplateValue({
                            short_description: `Review for featured status: ${wfa.dataPill(article.Record.short_description, 'string')}`,
                            assigned_to: wfa.dataPill(kbManager.Record.sys_id, 'reference'),
                            priority: 4,
                            state: 1,
                        }),
                    }
                )
            }
        )

        wfa.action(
            action.core.sendNotification,
            { $id: Now.ID['notify_author_approved'] },
            {
                record: wfa.dataPill(article.Record.sys_id, 'reference'),
                notification: 'kb_article_qa_approved',
            }
        )
    }
)

```

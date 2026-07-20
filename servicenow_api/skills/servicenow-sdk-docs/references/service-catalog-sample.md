# Service Catalog Sample

This is a sample of using the various `ServiceCatalog` APIs available in the ServiceNow SDK

## Example Location
Source Code: [assets/samples/service-catalog-sample](../assets/samples/service-catalog-sample)

## Code Samples

### `sc-record-producer.now.ts`
Path: [service-catalog-sample/fluent/sc-record-producer.now.ts](../assets/samples/service-catalog-sample/fluent/sc-record-producer.now.ts)

```typescript
import {
    CatalogItemRecordProducer,
    CatalogUiPolicy,
    CatalogClientScript,
    SingleLineTextVariable,
    MultiLineTextVariable,
    SelectBoxVariable,
    DateTimeVariable,
    AttachmentVariable,
    ReferenceVariable,
    Role,
    Table,
    StringColumn,
} from '@servicenow/sdk/core'

// ---------------------------------------------------------------------------
// Roles
// ---------------------------------------------------------------------------

const itil = Role({ name: 'x_servicecatalog.fulfiller' })

// ---------------------------------------------------------------------------
// Record Producer – Report an Incident
// ---------------------------------------------------------------------------

export const reportIncidentProducer = CatalogItemRecordProducer({
    $id: Now.ID['report_incident_producer'],
    name: 'Report an Incident',
    shortDescription: 'Quickly report a new incident from the service catalog',
    table: 'incident',
    state: 'published',
    availability: 'both',
    roles: [itil],

    // Record producer settings
    redirectUrl: 'generatedRecord',
    canCancel: true,

    variables: {
        short_desc: SingleLineTextVariable({
            question: 'Brief summary of the issue',
            order: 100,
            mandatory: true,
            mapToField: true,
            field: 'short_description',
        }),

        urgency: SelectBoxVariable({
            question: 'Urgency',
            order: 200,
            mandatory: true,
            choices: {
                '1': { label: 'High' },
                '2': { label: 'Medium' },
                '3': { label: 'Low' },
            },
            defaultValue: '2',
            mapToField: true,
            field: 'urgency',
        }),

        assigned_to: ReferenceVariable({
            question: 'Assign To',
            order: 250,
            referenceTable: 'sys_user',
            useReferenceQualifier: 'simple',
            referenceQualCondition: 'active=true',
            mapToField: true,
            field: 'assigned_to',
        }),

        affected_date: DateTimeVariable({
            question: 'When did the issue start?',
            order: 300,
        }),

        detail: MultiLineTextVariable({
            question: 'Detailed Description',
            order: 400,
            mapToField: true,
            field: 'description',
        }),

        screenshot: AttachmentVariable({
            question: 'Attach a screenshot (optional)',
            order: 500,
        }),
    },
})

// ---------------------------------------------------------------------------
// UI Policy – Hide screenshot when urgency is low
// ---------------------------------------------------------------------------

export const hideScreenshotForLowUrgency = CatalogUiPolicy({
    $id: Now.ID['hide_screenshot_low_urgency_policy'],
    shortDescription: 'Hide screenshot upload when urgency is low',
    catalogItem: reportIncidentProducer,
    active: true,
    onLoad: true,
    reverseIfFalse: true,
    catalogCondition: `${reportIncidentProducer.variables.short_desc}=catalogitem^${reportIncidentProducer.variables.assigned_to}ISNOTEMPTY^EQ`,
    appliesOnCatalogItemView: true,
    appliesOnRequestedItems: true,
    order: 300,
    actions: [
        {
            variableName: reportIncidentProducer.variables.screenshot,
            visible: false,
        },
    ],
})

// ---------------------------------------------------------------------------
// Client Script – Validate description on submit
// ---------------------------------------------------------------------------

export const incidentSubmitValidation = CatalogClientScript({
    $id: Now.ID['incident_submit_validation_script'],
    name: 'Validate incident description length on submit',
    catalogItem: reportIncidentProducer,
    type: 'onSubmit',
    active: true,
    uiType: 'all',
    appliesOnCatalogItemView: true,
    script: `
function onSubmit() {
    var urgency = g_form.getValue('urgency');
    var detail = g_form.getValue('detail');
    if (urgency === '1' && (!detail || detail.length < 20)) {
        g_form.addErrorMessage('High urgency incidents require a detailed description (at least 20 characters).');
        return false;
    }
    return true;
}`,
})

// ---------------------------------------------------------------------------
// Client Script – Auto-set short description prefix based on urgency
// ---------------------------------------------------------------------------

export const incidentUrgencyChangeScript = CatalogClientScript({
    $id: Now.ID['incident_urgency_change_script'],
    name: 'Auto-set short description prefix based on urgency',
    catalogItem: reportIncidentProducer,
    type: 'onChange',
    variableName: reportIncidentProducer.variables.urgency,
    active: true,
    uiType: 'all',
    appliesOnCatalogItemView: true,
    script: `
function onChange(control, oldValue, newValue, isLoading) {
    if (isLoading) return;
    var shortDesc = g_form.getValue('short_desc');
    var prefixes = { '1': '[HIGH] ', '2': '[MEDIUM] ', '3': '[LOW] ' };
    // Remove any existing prefix
    shortDesc = shortDesc.replace(/^\\[(HIGH|MEDIUM|LOW)\\] /, '');
    if (prefixes[newValue]) {
        g_form.setValue('short_desc', prefixes[newValue] + shortDesc);
    }
}`,
})

export const x_servicecatalog_security_incident = Table({
    allowWebServiceAccess: true,
    label: 'Security incident',
    name: 'x_servicecatalog_security_incident',
    schema: {
        name: StringColumn({
            label: 'Name',
        }),
        description: StringColumn({
            label: 'Description',
        }),
    },
})

export const reportSecurityIncidentProducer = CatalogItemRecordProducer({
    $id: Now.ID['report_security_incident_producer'],
    name: 'Report an Incident',
    shortDescription: 'Quickly report a new incident from the service catalog',
    table: x_servicecatalog_security_incident.name,
    state: 'published',
    availability: 'both',

    // Record producer settings
    redirectUrl: 'generatedRecord',
    canCancel: true,

    variables: {
        short_desc: SingleLineTextVariable({
            question: 'Brief summary of the issue',
            order: 100,
            mandatory: true,
            mapToField: true,
            field: 'description',
        }),
    },
})

```

### `sc-full-example.now.ts`
Path: [service-catalog-sample/fluent/sc-full-example.now.ts](../assets/samples/service-catalog-sample/fluent/sc-full-example.now.ts)

```typescript
import {
    CatalogItem,
    Record,
    VariableSet,
    SingleLineTextVariable,
    MultiLineTextVariable,
    ReferenceVariable,
    RequestedForVariable,
    SelectBoxVariable,
    EmailVariable,
} from '@servicenow/sdk/core'

// ---------------------------
// Variable Sets
// ---------------------------
const userInfoVarSet = VariableSet({
    $id: Now.ID['user_info_varset'],
    title: 'User Information',
    description: 'Basic user information required for this request',
    internalName: 'user_info_varset',
    type: 'singleRow',
    layout: 'normal',
    order: 100,
    displayTitle: true,
    version: 4,
    variables: {
        userName: ReferenceVariable({
            question: 'User Name',
            referenceTable: 'sys_user',
            mandatory: true,
            order: 100,
            tooltip: 'user name',
        }),
        userEmail: EmailVariable({
            question: 'Email Address',
            mandatory: true,
            order: 200,
        }),
        userPhone: SingleLineTextVariable({
            question: 'Phone Number',
            order: 300,
        }),
    },
    name: 'User information',
})

const hardwareSpecsVarSet = '3820df570a0a0b2700d944110d29fc55'

// ---------------------------
// Catalogs
// ---------------------------
const catalogServiceCatalog = 'e0d08b13c3330100c8b837659bba8fb4'
const catalogTechnicalCatalog = Record({
    $id: Now.ID['technical_catalog'],
    table: 'sc_catalog',
    data: {
        title: 'Enterprise IT Catalog',
        description: 'Enterprise IT services and infrastructure items',
        active: true,
        desktop_home_page: 'welcome',
        enable_cart: true,
        enable_wish_list: true,
        manager_role: 'admin',
        sys_domain: 'global',
    },
})

// ---------------------------
// Categories
// ---------------------------
const categoryHardware = 'd258b953c611227a0146101fb1be7c31'
const categorySoftware = Record({
    $id: Now.ID['software_category'],
    table: 'sc_category',
    data: {
        title: 'Software',
        description: 'Software related items',
        catalog: catalogTechnicalCatalog,
        active: true,
        order: 100,
        sys_domain: 'global',
    },
})

// ---------------------------
// Topics
// ---------------------------
const topicHardware = '782413a7c3053010069aec4b7d40ddf1'
const topicSoftware = Record({
    $id: Now.ID['software_topic'],
    table: 'topic',
    data: {
        name: 'Software',
        description: 'Software related knowledge articles',
        taxonomy: '1f5d5a40c3203010069aec4b7d40dd93',
        active: true,
        sys_domain: 'global',
    },
})

// ---------------------------
// User Criteria
// ---------------------------
const userCriteriaItilRole = 'afbaf8be844d40d7a526798fd6ecc5f8'
const userCriteriaDevDepartment = Record({
    $id: Now.ID['dev_department_criteria'],
    table: 'user_criteria',
    data: {
        name: 'Development Department Access',
        short_description: 'User criteria for Development department members',
        script: 'current.department.name == "Development";',
        active: true,
        match_all: false,
        advanced: true,
        sys_domain: 'global',
    },
})

// ---------------------------
// Example 1: Basic Catalog Item
// ---------------------------
export const basicLaptopRequest = CatalogItem({
    $id: Now.ID['basic_catalog_item'],
    name: 'Basic Laptop Request',
    shortDescription: 'Request a standard laptop for business use',
    description: 'Use this form to request a standard laptop for business use. Approval from your manager is required.',
    catalogs: [catalogServiceCatalog],
    categories: [categoryHardware],
    variableSets: [{ variableSet: userInfoVarSet, order: 100 }],
    executionPlan: '523da512c611228900811a37c97c2014',
})

// ---------------------------
// Example 2: Catalog Item with Pricing
// ---------------------------
export const pricedDeveloperWorkstation = CatalogItem({
    $id: Now.ID['priced_catalog_item'],
    name: 'Developer Workstation',
    shortDescription: 'High-performance developer workstation',
    description: 'Complete developer workstation with dual monitors, docking station, and peripherals.',
    catalogs: [catalogServiceCatalog],
    categories: [categoryHardware],
    cost: 1500,
    pricingDetails: [
        { amount: 1500, currencyType: 'USD', field: 'price' },
        { amount: 100, currencyType: 'USD', field: 'recurring_price' },
    ],
    variableSets: [{ variableSet: userInfoVarSet, order: 100 }],
    executionPlan: '523da512c611228900811a37c97c2014',
    variables: {
        shortDescription: SingleLineTextVariable({
            order: 1,
            question: 'Short Description',
        }),
        laptopType: SelectBoxVariable({
            order: 4,
            question: 'Laptop Type',
            mandatory: true,
            choices: {
                standard: { label: 'Standard Business Laptop' },
                performance: { label: 'Performance Laptop (Development/Design)' },
                executive: { label: 'Executive Laptop' },
                workstation: { label: 'Mobile Workstation' },
            },
            defaultValue: 'standard',
            tooltip: 'Select the type of laptop based on your work requirements',
        }),
    },
})

// ---------------------------
// Example 3: Catalog Item with Topics and Access Controls
// ---------------------------
export const softwareInstallation = CatalogItem({
    $id: Now.ID['topic_catalog_item'],
    name: 'Software Installation',
    shortDescription: 'Request software installation',
    description: 'Use this form to request installation of software on your company device.',
    catalogs: [catalogTechnicalCatalog],
    categories: [categorySoftware],
    assignedTopics: [topicSoftware, topicHardware],
    meta: ['software', 'installation', 'IT'],
    accessType: 'restricted',
    availableFor: [userCriteriaItilRole],
    notAvailableFor: [userCriteriaDevDepartment],
    variableSets: [
        { variableSet: userInfoVarSet, order: 100 },
        { variableSet: hardwareSpecsVarSet, order: 200 },
    ],
    executionPlan: '523da512c611228900811a37c97c2014',
    useScLayout: true,
    deliveryPlanScript: `// Custom delivery plan logic
gs.info('Processing delivery plan for software installation');`,
    entitlementScript: `// Entitlement check
return current.department.name == 'IT' || current.hasRole('admin');`,
    image: 'software_icon.png',
    icon: 'icon-software',
    roles: ['itil', 'admin'],
    variables: {
        shortDescription: SingleLineTextVariable({
            order: 1,
            question: 'Short Description',
        }),
        description: MultiLineTextVariable({
            order: 2,
            question: 'Description',
        }),
        name: RequestedForVariable({
            order: 3,
            question: 'Requested For',
        }),
        active_user: SingleLineTextVariable({
            order: 4,
            question: 'Active',
        }),
        company: ReferenceVariable({
            order: 5,
            question: 'Company',
            referenceTable: 'core_company',
        }),
    },
})

```

### `sc-catalog-item.now.ts`
Path: [service-catalog-sample/fluent/sc-catalog-item.now.ts](../assets/samples/service-catalog-sample/fluent/sc-catalog-item.now.ts)

```typescript
import {
    CatalogItem,
    CatalogUiPolicy,
    CatalogClientScript,
    SelectBoxVariable,
    MultipleChoiceVariable,
    ReferenceVariable,
    DateVariable,
    YesNoVariable,
    MultiLineTextVariable,
    CheckboxVariable,
    AttachmentVariable,
    ContainerStartVariable,
    ContainerSplitVariable,
    ContainerEndVariable,
    MaskedVariable,
    NumericScaleVariable,
    ListCollectorVariable,
    Role,
} from '@servicenow/sdk/core'
import { Flow, wfa, trigger } from '@servicenow/sdk/automation'
import { contactInfoVariableSet } from './variable-set.now'

// ---------------------------------------------------------------------------
// Roles
// ---------------------------------------------------------------------------

const itil = Role({ name: 'x_servicecatalog.itil' })

// ---------------------------------------------------------------------------
// Flow – Laptop Request Fulfillment
// ---------------------------------------------------------------------------

export const laptopFulfillmentFlow = Flow(
    {
        $id: Now.ID['laptop_fulfillment_flow'],
        name: 'Laptop Request Fulfillment',
        description: 'Triggers when a laptop request item is created.',
        runAs: 'system',
        runWithRoles: [],
        flowPriority: 'LOW',
    },
    wfa.trigger(
        trigger.record.created,
        { $id: Now.ID['laptop_request_trigger'], annotation: 'Trigger when request item is created' },
        {
            table: 'sc_req_item',
            condition: '',
            run_on_extended: 'false',
            run_flow_in: 'background',
            run_when_user_list: [],
            run_when_setting: 'both',
            run_when_user_setting: 'any',
        }
    ),
    (_trigger) => {
        // Flow logic goes here
    }
)

// ---------------------------------------------------------------------------
// Catalog Item – Laptop Request
// ---------------------------------------------------------------------------

export const laptopRequest = CatalogItem({
    $id: Now.ID['laptop_request_catalog_item'],
    name: 'Laptop Request',
    shortDescription: 'Request a new laptop for an employee',
    description:
        'Use this catalog item to request a standard or high-performance laptop. Includes options for OS, accessories, and justification.',
    availability: 'both',
    order: 100,

    // Fulfillment
    fulfillmentAutomationLevel: 'semiAutomated',
    flow: laptopFulfillmentFlow,

    // Pricing
    ignorePrice: false,
    cost: 1200,
    recurringFrequency: 'yearly',
    billable: true,

    // Portal settings
    requestMethod: 'order',
    hideAddToCart: false,
    hideQuantitySelector: true,
    mandatoryAttachment: false,

    // Visibility
    visibleBundle: true,
    visibleGuide: true,
    visibleStandalone: true,

    // Access
    roles: [itil],

    // M2M relationships
    variableSets: [{ variableSet: contactInfoVariableSet, order: 0 }],

    // Variables
    variables: {
        // -- Container: Laptop Details --
        laptop_details_start: ContainerStartVariable({
            question: 'Laptop Details',
            displayTitle: true,
            layout: '2across',
            order: 1000,
        }),

        laptop_type: SelectBoxVariable({
            question: 'Laptop Type',
            order: 1100,
            mandatory: true,
            choices: {
                standard: { label: 'Standard (Business)' },
                performance: { label: 'High Performance (Engineering)' },
                ultrabook: { label: 'Ultrabook (Executive)' },
            },
            includeNone: false,
        }),

        operating_system: MultipleChoiceVariable({
            question: 'Operating System',
            order: 1200,
            mandatory: true,
            choices: {
                windows: { label: 'Windows 11 Pro' },
                macos: { label: 'macOS Sonoma' },
                linux: { label: 'Ubuntu 24.04 LTS' },
            },
            choiceDirection: 'down',
        }),

        laptop_details_split: ContainerSplitVariable({ order: 1300 }),

        needed_by: DateVariable({
            question: 'Date Needed By',
            order: 1400,
        }),

        assigned_user: ReferenceVariable({
            question: 'Assign To',
            order: 1500,
            referenceTable: 'sys_user',
            useReferenceQualifier: 'simple',
            referenceQualCondition: 'active=true',
        }),

        laptop_details_end: ContainerEndVariable({ order: 1600 }),

        // -- Additional Options --
        include_dock: YesNoVariable({
            question: 'Include Docking Station?',
            order: 2000,
            defaultValue: true,
        }),

        accessories: ListCollectorVariable({
            question: 'Additional Accessories',
            order: 2100,
            listTable: 'sc_cat_item',
            referenceQual: 'category=accessories',
        }),

        asset_tag_label: MaskedVariable({
            question: 'Previous Asset Tag (if replacing)',
            order: 2200,
            useConfirmation: true,
        }),

        satisfaction: NumericScaleVariable({
            question: 'How urgent is this request? (1-5)',
            order: 2300,
            scaleMin: 1,
            scaleMax: 5,
        }),

        justification: MultiLineTextVariable({
            question: 'Business Justification',
            order: 2400,
            mandatory: true,
        }),

        terms_accepted: CheckboxVariable({
            question: 'I accept the IT equipment usage policy',
            order: 2500,
            selectionRequired: true,
        }),

        supporting_doc: AttachmentVariable({
            question: 'Supporting Documentation',
            order: 2600,
        }),
    },
})

// ---------------------------------------------------------------------------
// UI Policy – Show dock option only for standard laptops
// ---------------------------------------------------------------------------

export const showDockForStandard = CatalogUiPolicy({
    $id: Now.ID['show_dock_for_standard_policy'],
    shortDescription: 'Show docking station option only for standard laptops',
    catalogItem: laptopRequest,
    active: true,
    onLoad: true,
    reverseIfFalse: true,
    catalogCondition: `${laptopRequest.variables.laptop_type}=standard^${laptopRequest.variables.assigned_user}ISNOTEMPTY^EQ`,
    appliesOnCatalogItemView: true,
    appliesOnRequestedItems: true,
    order: 100,
    actions: [
        {
            variableName: laptopRequest.variables.include_dock,
            visible: true,
        },
    ],
})

// ---------------------------------------------------------------------------
// Client Script – Auto-fill justification hint on type change
// ---------------------------------------------------------------------------

export const laptopTypeChangeScript = CatalogClientScript({
    $id: Now.ID['laptop_type_change_script'],
    name: 'Auto-set justification hint on laptop type change',
    catalogItem: laptopRequest,
    type: 'onChange',
    variableName: laptopRequest.variables.laptop_type,
    active: true,
    uiType: 'all',
    appliesOnCatalogItemView: true,
    script: Now.include('./sc-catalog-item.client.js'),
})

// ---------------------------------------------------------------------------
// Client Script – Set default needed-by date on load
// ---------------------------------------------------------------------------

export const laptopOnLoadScript = CatalogClientScript({
    $id: Now.ID['laptop_onload_script'],
    name: 'Set default needed-by date to 2 weeks from today',
    catalogItem: laptopRequest,
    type: 'onLoad',
    active: true,
    uiType: 'all',
    appliesOnCatalogItemView: true,
    script: `
function onLoad() {
    var today = new Date();
    today.setDate(today.getDate() + 14);
    var defaultDate = today.toISOString().split('T')[0];
    g_form.setValue('needed_by', defaultDate);
}`,
})

```

### `variable-set.now.ts`
Path: [service-catalog-sample/fluent/variable-set.now.ts](../assets/samples/service-catalog-sample/fluent/variable-set.now.ts)

```typescript
import {
    VariableSet,
    CatalogUiPolicy,
    CatalogClientScript,
    SingleLineTextVariable,
    EmailVariable,
    Role,
} from '@servicenow/sdk/core'

// ---------------------------------------------------------------------------
// Roles
// ---------------------------------------------------------------------------

const itil = Role({ name: 'x_servicecatalog.requestor' })

// ---------------------------------------------------------------------------
// Reusable Variable Set – Contact Information
// ---------------------------------------------------------------------------

export const contactInfoVariableSet = VariableSet({
    $id: Now.ID['contact_info_variable_set'],
    title: 'Contact Information',
    description: 'Reusable set of contact-related variables',
    type: 'singleRow',
    layout: '2across',
    displayTitle: true,
    order: 100,
    readRoles: [itil],
    variables: {
        contact_name: SingleLineTextVariable({
            question: 'Full Name',
            order: 100,
            mandatory: true,
        }),
        contact_email: EmailVariable({
            question: 'Email Address',
            order: 200,
            mandatory: true,
        }),
        contact_phone: SingleLineTextVariable({
            question: 'Phone Number',
            order: 300,
            validateRegex: '/^\\+?[0-9\\-\\s]+$/',
        }),
    },
})

// ---------------------------------------------------------------------------
// UI Policy – Make phone mandatory when email is provided
// ---------------------------------------------------------------------------

export const contactPhoneMandatoryPolicy = CatalogUiPolicy({
    $id: Now.ID['contact_phone_mandatory_policy'],
    shortDescription: 'Make phone number mandatory when email is provided',
    variableSet: contactInfoVariableSet,
    appliesTo: 'set',
    active: true,
    onLoad: true,
    reverseIfFalse: true,
    catalogCondition: `${contactInfoVariableSet.variables.contact_name}=email^${contactInfoVariableSet.variables.contact_email}ISNOTEMPTY^EQ`,
    appliesOnCatalogItemView: true,
    appliesOnRequestedItems: true,
    order: 200,
    actions: [
        {
            variableName: contactInfoVariableSet.variables.contact_phone,
            mandatory: true,
        },
    ],
})

// ---------------------------------------------------------------------------
// Client Script – Auto-format phone number on change
// ---------------------------------------------------------------------------

export const contactPhoneFormatScript = CatalogClientScript({
    $id: Now.ID['contact_phone_format_script'],
    name: 'Auto-format phone number in contact info',
    variableSet: contactInfoVariableSet,
    appliesTo: 'set',
    type: 'onChange',
    variableName: contactInfoVariableSet.variables.contact_phone,
    active: true,
    uiType: 'all',
    appliesOnCatalogItemView: true,
    script: `
function onChange(control, oldValue, newValue, isLoading) {
    if (isLoading) return;
    var digits = newValue.replace(/\\D/g, '');
    if (digits.length === 10) {
        var formatted = '(' + digits.substring(0, 3) + ') ' + digits.substring(3, 6) + '-' + digits.substring(6);
        g_form.setValue('contact_phone', formatted);
    }
}`,
})

```

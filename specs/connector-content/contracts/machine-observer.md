# Machine observer link

Provider: scion-sdk SCION-CENTRALIZED-CAPABILITIES-R057.1
Consumer: servicenow-api CONN-SERVICENOW-API-CONNECTOR-CONTENT-R012.1

## Wire shape

A connector record that describes a machine states `core:observes` to the key anchor of a key it holds. The target id is `urn:machine-key:<kind>:<first 32 hex of sha256(kind LF value)>`, which the SDK helper `observes_machine` returns. The kind is `uuid`, `serial`, `bmc` or `host`. The connector resource lists the relation `observes` with target `MachineKey` in its declaration. The connector class itself rolls up as `rdfs:subClassOf core:Machine`, and the pack never imports the core ontology.

## Refusal codes

- `MachineKeyRefused`: the key is malformed or a placeholder. The connector skips that link and still writes the record.
- The engine shape of `core:MachineKey` refuses an anchor that does not match its id pattern.

## Authoritative types

- `scion_sdk/machine.py` in scion-sdk: `observes_machine`, `OBSERVES_RELATION`, `MachineKeyRefused`.
- `crates/medulla-core/ontology/machine-v1.ttl` in medulla: `core:observes`, `core:MachineKey`.

## Test vectors

- The five key anchor vectors in the `data-model.md` of `MEDULLA-MACHINE`.
- `tests/test_machine_observer.py::test_observes_machine_targets_the_key_anchor_of_the_vector` in scion-sdk.

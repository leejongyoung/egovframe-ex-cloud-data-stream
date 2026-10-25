# egovframe-ex-cloud-data-stream: project context

## Role and maintenance boundary

Spring Cloud Stream publisher/subscriber examples spanning R2DBC, MongoDB, messaging, and IoT inputs. Preserve message payloads, binder/destination configuration, publisher/subscriber boundaries, and the documented example setup.
This card reflects source inspection at adoption; it does not certify runtime behavior.

## Public entry points and evidence

- `README.md`: architecture, five stream examples, Docker networks, setup order, Java 17+, Maven 3.9+, and hardware requirements.
- `ex-egovframe-stream-pub-r2dbc/pom.xml` and `ex-egovframe-stream-sub-mongodb/pom.xml`: Java 17, eGovFrame Boot parent 5.0.1, Kafka/Rabbit binders and reactive persistence.
- `egovframe-cloud-stream-test/pom.xml`: a separate Maven example/test module; there is no root reactor POM.
- `DOCKER/*/docker-compose.yml`: explicit external infrastructure; `IOT/` contains the sensor example.

## Build and verification entry points

From the repository root, `mvn -f ex-egovframe-stream-pub-r2dbc/pom.xml test`,
`mvn -f ex-egovframe-stream-sub-mongodb/pom.xml test`, and
`mvn -f egovframe-cloud-stream-test/pom.xml test` are manifest-derived Maven entry points,
not checks executed during adoption. For integration work follow the Docker startup order in
README: Kafka and OpenSearch establish networks before dependent services. Validate actual
message delivery separately; a unit-test command cannot demonstrate broker interoperability.

## Environment and evidence limits

README requires Docker, Java 17+, Maven 3.9+, and for IoT Python 3.9.2+ with Raspberry Pi
and a sensor. Broker hosts and network settings are environment-dependent. Keep actual
credentials outside version control; the documented demonstration defaults are not production
configuration. Do not start Docker services for tooling adoption.
No application build, test suite, formatter, device test, or external service was run for this
workflow-only adoption. A Spec Kit CLI/status and isolated scaffold smoke validate the tooling
only. No CodeGraph index was present in the adoption workspace; targeted file listing and
exact text inspection supplied the evidence, without installing an indexer.

## Upstream and submission baseline

Upstream: [eGovFramework/egovframe-ex-cloud-data-stream](https://github.com/eGovFramework/egovframe-ex-cloud-data-stream). Fetch the actual upstream default branch
and record its exact SHA before preparing `upstream-submit`; do not infer the baseline from
fork work. Preserve an existing submission branch or open PR. Adoption changes are pushed
only to fork `work`; an absent `upstream-submit` is created from the fetched upstream SHA
without adoption commits, as a separate submission baseline.
The [constitution](constitution.md) is the policy source for domain cards, verification, and
work-only artifact isolation. Native OMP commands are in `.omp/commands/`; the bundled bug
workflow provides assess, fix, and test stages. No application fix or PR is part of
this adoption.

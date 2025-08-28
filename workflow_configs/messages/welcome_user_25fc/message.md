👋 Welcome to Cyoda Application Builder! Let’s build something working together! We are going to go through the following steps:

```mermaid
graph TD
    A([Finalize App Requirements]):::bar e1@== build_general_application
    ==> B([Deploy Cyoda environment]):::bar
    B e2@== deploy_cyoda_env ==> C([Gen Entities & Workflows]):::bar
    C e3@== functional_requirements_to_prototype ==> D([Gen Controllers, Processors, Criteria & Tests]):::bar
    D e4@== init_setup_workflow ==> E([Launch Cyoda App]):::bar

    e1@{ animate: true }
    e2@{ animate: true }
    e3@{ animate: true }
    e4@{ animate: true }
    classDef bar stroke:#0D8484
```
   
   
🧐 Learn more about Cyoda on [Our website](https://cyoda.com) and [Docs](https://docs.cyoda.net)

👋 Welcome to Cyoda Application Builder (Optimized flow)!

I will go through the following steps on my own. 

This will take from 10 to 30 minutes depending on the complexity of the application.

**Please make sure you've logged in to your account so that we could prepare your environment.**

```mermaid
graph TD
    %% Nodes
    B([🔒 Deploy Cyoda environment]):::bar e1@== deploy_cyoda_env ==> C([🔒 Gen Entities & Workflows]):::bar
    C e3@== functional_requirements_to_prototype ==> D([🔒 Gen Controllers, Processors, Criteria]):::bar
    D e4@== init_setup_workflow ==> E([🔒 Launch Cyoda App]):::bar

    %% Animations (original event markers)
    e1@{ animate: true }
    e3@{ animate: true }
    e4@{ animate: true }

    %% Styles (transparent nodes, teal accents)
    classDef bar fill:transparent,stroke:#0D8484,stroke-width:2px,rx:12,ry:12
    linkStyle default stroke:#0D8484,stroke-width:2px,opacity:0.95
``` 
  
Once the application is ready, I will start launch assistant, so that we can start your application together.

🧐 Learn more about Cyoda on [Our website](https://cyoda.com) and [Docs](https://docs.cyoda.net)

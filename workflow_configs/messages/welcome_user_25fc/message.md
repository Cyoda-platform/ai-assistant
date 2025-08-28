👋 Welcome to Cyoda Application Builder! Let’s build something working together! We are going to go through the following steps:

```mermaid
%% Brand theming + polish
%% - Teal accents (#0D8484)
%% - Rounded nodes, subtle fill, readable font
%% - Consistent edge styling
%% - Emoji icons for quick scanning (optional—remove if you prefer)
%% You can switch to `graph LR` for horizontal; kept TD per your snippet.
%%{init: {'theme':'base','themeVariables':{
  'primaryColor':'#ECF8F8',
  'primaryTextColor':'#083A3A',
  'primaryBorderColor':'#0D8484',
  'lineColor':'#0D8484',
  'fontFamily':'Inter, Arial, sans-serif',
  'edgeLabelBackground':'#FFFFFF'
}}}%%
graph TD
    %% Nodes
    A([🔒 Finalize App Requirements]):::bar e1@== build_general_application
    ==> B([🔒 Deploy Cyoda environment]):::bar
    B e2@== deploy_cyoda_env ==> C([🔒 Gen Entities & Workflows]):::bar
    C e3@== functional_requirements_to_prototype ==> D([🔒 Gen Controllers, Processors, Criteria & Tests]):::bar
    D e4@== init_setup_workflow ==> E([🔒 Launch Cyoda App]):::bar

    %% Animations (your original event markers)
    e1@{ animate: true }
    e2@{ animate: true }
    e3@{ animate: true }
    e4@{ animate: true }

    %% Styles
    classDef bar fill:#ECF8F8,stroke:#0D8484,stroke-width:2px,rx:10,ry:10,color:#083A3A
    linkStyle default stroke:#0D8484,stroke-width:2px,opacity:0.95

```   
   
🧐 Learn more about Cyoda on [Our website](https://cyoda.com) and [Docs](https://docs.cyoda.net)

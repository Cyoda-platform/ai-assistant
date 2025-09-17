Next up: functional requirements.
It will take me up to 10 mins to add requirements to `src/main/resources/functional_requirements/` directory.
I will add separate files for entities, workflows, processors, criteria and controllers.

Stay tuned — thoughtful thinking in progress. 🧠✨

```mermaid
%%{init: {'theme':'base','themeVariables':{
  'primaryColor':'#ECF8F8','primaryTextColor':'#083A3A','primaryBorderColor':'#0D8484',
  'lineColor':'#0D8484','fontFamily':'Inter, Arial, sans-serif','edgeLabelBackground':'#FFFFFF'
}}}%%
graph LR
    S((Start)):::start e0@ ==> A([🧚 Finalize App Requirements]):::next
    A e1@ ==> B([🔒 Deploy Cyoda environment]):::bar
    B e2@ ==> C([🔒 Gen Entities & Workflows]):::bar
    C e3@ ==> D([🔒 Gen Controllers, Processors, Criteria & Tests]):::bar
    D e4@ ==> E([🔒 Launch Cyoda App]):::bar

    %% animate incoming to the next step (A)
    e0@{ animate: true }

    classDef start fill:#FFFFFF,stroke:#0D8484,stroke-width:2px,color:#083A3A
    classDef bar   fill:#ECF8F8,stroke:#0D8484,stroke-width:2px,rx:12,ry:12,color:#083A3A
    classDef done  fill:#0D8484,stroke:#0D8484,stroke-width:2px,rx:12,ry:12,color:#FFFFFF
    classDef next  fill:#FFFFFF,stroke:#0D8484,stroke-width:3px,stroke-dasharray:6 4,rx:12,ry:12,color:#083A3A
    linkStyle default stroke:#0D8484,stroke-width:2px,opacity:0.95

```

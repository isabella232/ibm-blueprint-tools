## 8. How to visualize the `blueprint configuration file` ?

While developing the blueprint configuration - that comprise of mutiple modules and dependencies between them - it can become complex to draw a mental picture of the overall cloud environment or architecture.

What-if, you are able to visualize the blueprint configuration in the following manner using the following tool:

> blueprint draw [-h] -b BP_FILE [-s SOURCE_DIR] [-o OUT_FILE] [-f {png,jpg,svg,pdf,dot}] [-l LOG_FILE]
                              [-e {DEBUG,INFO,WARNING,ERROR}]

A graphviz network diagram
![Blueprint GraphViz diagram](./images/sample_bp_viz.png?raw=true "Sample Blueprint visualization - viz")


A schemedraw circuit diagram
![Blueprint Circuit diagram](./images/sample_bp_ic.png?raw=true "Sample Blueprint visualization - viz")


---
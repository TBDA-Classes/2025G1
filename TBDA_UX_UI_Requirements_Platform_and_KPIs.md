# UX/UI Requirements Specification -- CNC Data Analysis Platform {#uxui-requirements-specification-cnc-data-analysis-platform .unnumbered}

## 1. Objective of the User Interface {#objective-of-the-user-interface .unnumbered}

The user interface shall transform complex, high-frequency machine data
into comprehensible, actionable information. It supports monitoring,
analysis, and interpretation of machine behavior with focus on
operational states (Running / Idle / Alarm), energy consumption, program
execution, and contextual alerts. The UI must be intuitive, responsive,
and insight-driven.

## 2. Target Users and Usage Context {#target-users-and-usage-context .unnumbered}

  -----------------------------------------------------------------------
  **User Group**          **Goals / Tasks**       **Usage Context**
  ----------------------- ----------------------- -----------------------
  Machine Operator        Monitor real-time       Shop floor environment;
                          machine state; detect   touch display.
                          alerts.                 

  Process / Production    Analyze energy usage;   Office or control room.
  Engineer                review program          
                          duration; optimize      
                          process.                

  Maintenance Technician  Analyze and trace       Workshop; possible
                          alarms; investigate     mobile use.
                          failures.               

  Management / Production Get overview of         Dashboard view in
  Lead                    utilization; review     office.
                          efficiency KPIs.        
  -----------------------------------------------------------------------

##  {#section .unnumbered}

## 3. Functional UX/UI Requirements {#functional-uxui-requirements .unnumbered}

### 3.1 Dashboard Design {#dashboard-design .unnumbered}

  -----------------------------------------------------------------------
  **Requirement**         **Description**         **Priority**
  ----------------------- ----------------------- -----------------------
  Real-time Status        Show current machine    High
                          state (Running, Idle,   
                          Alarm) using clear      
                          color coding.           

  KPI Widgets             Display key metrics:    High
                          runtime, energy use,    
                          alarms, and program     
                          information.            

  Interactive Charts      Zoomable time-series    High
                          plots with tooltips and 
                          markers.                

  Customizable Dashboard  Allow users to add,     Medium
                          move, or remove         
                          widgets.                

  Machine Overview (Fleet Show status and energy  Medium
  View)                   consumption of multiple 
                          machines.               

  Dark/Light Mode         Adaptable to            Low
                          environment (shop floor 
                          vs. office).            
  -----------------------------------------------------------------------

###  {#section-1 .unnumbered}

### 3.2 Data Analysis View {#data-analysis-view .unnumbered}

  -----------------------------------------------------------------------
  **Requirement**         **Description**         **Priority**
  ----------------------- ----------------------- -----------------------
  Timeline Visualization  Display machine         High
                          operation periods as    
                          colored bands (Running, 
                          Idle, Alarm).           

  Program-based Analysis  Filter and visualize    High
                          data by program name.   

  Energy Analysis         Show energy consumption High
                          per program or time     
                          frame.                  

  Comparison View         Compare performance,    Medium
                          energy, or duration     
                          across programs or      
                          periods.                

  Drill-down Function     Clicking data points    High
                          opens detailed analysis 
                          (parameters, alarms,    
                          time).                  

  Export Function         Export charts or tables Medium
                          (PNG, CSV, PDF).        
  -----------------------------------------------------------------------

###  {#section-2 .unnumbered}

### 3.3 Alarm and Event Management {#alarm-and-event-management .unnumbered}

  -----------------------------------------------------------------------
  **Requirement**         **Description**         **Priority**
  ----------------------- ----------------------- -----------------------
  Alarm Overview          List of active and past High
                          alarms with time,       
                          machine, and cause.     

  Alarm Context View      Show alarms within the  High
                          timeline and correlate  
                          with machine status.    

  Filtering & Sorting     Filter by type, time    Medium
                          range, or severity.     

  Acknowledge & Comment   Allow operators to      Medium
                          acknowledge and add     
                          comments to alarms.     

  Contextual Hints        Provide insights like   High
                          \'Alarm occurred during 
                          Tool Change\'.          
  -----------------------------------------------------------------------

### Concrete performance metrics  1. Machine Performance Indicators (Operational Efficiency) {#concrete-performance-metrics-1.-machine-performance-indicators-operational-efficiency .unnumbered}

### These measure how well the CNC or 5-axis machines are running. {#these-measure-how-well-the-cnc-or-5-axis-machines-are-running. .unnumbered}

+-----------------+-------------------+--------------------------------+
| ### KPI {#k     | ### Formu         | ### Why It's Important {#      |
| pi .unnumbered} | la / Description  | why-its-important .unnumbered} |
|                 | {#formula-descrip |                                |
|                 | tion .unnumbered} |                                |
+=================+===================+================================+
| ### Mach        | ### (Active mach  | ##                             |
| ine Utilization | ining time / Tota | # Shows how much the machines  |
|  Rate {#machine | l available time) | are actually used. Low utiliza |
| -utilization-ra |  × 100 {#active-m | tion = underused equipment or  |
| te .unnumbered} | achining-time-tot | downtime. {#shows-how-much-the |
|                 | al-available-time | -machines-are-actually-used.-l |
|                 | -100 .unnumbered} | ow-utilization-underused-equip |
|                 |                   | ment-or-downtime. .unnumbered} |
+-----------------+-------------------+--------------------------------+
| ##              | ###               | ### Global measure combi       |
| # Overall Equip |  Availability × P | ning uptime, speed, and qualit |
| ment Effectiven | erformance × Qual | y --- a key manufacturing KPI. |
| ess (OEE) {#ove | ity {#availabilit |  {#global-measure-combining-up |
| rall-equipment- | y-performance-qua | time-speed-and-quality-a-key-m |
| effectiveness-o | lity .unnumbered} | anufacturing-kpi. .unnumbered} |
| ee .unnumbered} |                   |                                |
+-----------------+-------------------+--------------------------------+
| #               | #                 | ### Identifies mai             |
| ## Downtime Rat | ## (Downtime hour | ntenance or setup issues reduc |
| e {#downtime-ra | s / Total hours)  | ing production. {#identifies-m |
| te .unnumbered} | × 100 {#downtime- | aintenance-or-setup-issues-red |
|                 | hours-total-hours | ucing-production. .unnumbered} |
|                 | -100 .unnumbered} |                                |
+-----------------+-------------------+--------------------------------+
| ### Cycle       | ### Average ti    | ### Helps evaluate             |
| Time {#cycle-ti | me to complete on |  efficiency and compare machin |
| me .unnumbered} | e machining opera | es or programs. {#helps-evalua |
|                 | tion {#average-ti | te-efficiency-and-compare-mach |
|                 | me-to-complete-on | ines-or-programs. .unnumbered} |
|                 | e-machining-opera |                                |
|                 | tion .unnumbered} |                                |
+-----------------+-------------------+--------------------------------+
| ### Spi         | ### R             | ### Detect                     |
| ndle Load / Pow | eal-time sensor d | s overloads, inefficiencies, o |
| er Consumption  | ata (if available | r maintenance needs. {#detects |
| {#spindle-load- | ) {#real-time-sen | -overloads-inefficiencies-or-m |
| power-consumpti | sor-data-if-avail | aintenance-needs. .unnumbered} |
| on .unnumbered} | able .unnumbered} |                                |
+-----------------+-------------------+--------------------------------+

###  2. Production Quality Indicators {#production-quality-indicators .unnumbered}

### These connect machine precision to output quality. {#these-connect-machine-precision-to-output-quality. .unnumbered}

+----------------+----------------------------+------------------------+
| ### KPI {#kpi- | ### Formul                 | ### Why It's           |
| 1 .unnumbered} | a / Description {#formula- | Important {#why-its-im |
|                | description-1 .unnumbered} | portant-1 .unnumbered} |
+================+============================+========================+
| ##             | ### (Number of defecti     | ### Tracks waste a     |
| # Scrap Rate / | ve parts / Total parts pro | nd cost of rework. {#t |
|  Rejection Rat | duced) × 100 {#number-of-d | racks-waste-and-cost-o |
| e {#scrap-rate | efective-parts-total-parts | f-rework. .unnumbered} |
| -rejection-rat | -produced-100 .unnumbered} |                        |
| e .unnumbered} |                            |                        |
+----------------+----------------------------+------------------------+
| ### Rework Rat | ### (Parts                 | ### Meas               |
| e {#rework-rat |  requiring re-machining /  | ures process stability |
| e .unnumbered} | Total parts) × 100 {#parts | . {#measures-process-s |
|                | -requiring-re-machining-to | tability. .unnumbered} |
|                | tal-parts-100 .unnumbered} |                        |
+----------------+----------------------------+------------------------+
| ### Fi         | ### (Goo                   | ### In                 |
| rst Pass Yield | d parts at first attempt / | dicates process capabi |
|  (FPY) {#first |  Total parts) × 100 {#good | lity and setup accurac |
| -pass-yield-fp | -parts-at-first-attempt-to | y. {#indicates-process |
| y .unnumbered} | tal-parts-100 .unnumbered} | -capability-and-setup- |
|                |                            | accuracy. .unnumbered} |
+----------------+----------------------------+------------------------+

## 3. Production & Throughput Indicators {#production-throughput-indicators .unnumbered}

### Measure overall manufacturing output and bottlenecks. {#measure-overall-manufacturing-output-and-bottlenecks. .unnumbered}

+-----------------+-------------------------+--------------------------+
| ### KPI {#kpi   | ### Formula / De        | ### Why I                |
| -2 .unnumbered} | scription {#formula-des | t's Important {#why-its- |
|                 | cription-2 .unnumbered} | important-2 .unnumbered} |
+=================+=========================+==========================+
| ### Produ       | #                       | ### Tracks out           |
| ction Volume {# | ## Number of parts prod | put trends. {#tracks-out |
| production-volu | uced per day/week {#num | put-trends. .unnumbered} |
| me .unnumbered} | ber-of-parts-produced-p |                          |
|                 | er-dayweek .unnumbered} |                          |
+-----------------+-------------------------+--------------------------+
| ### T           | ### Ti                  | ### Refl                 |
| hroughput Time  | me from raw material to | ects production efficien |
| {#throughput-ti |  finished part {#time-f | cy end-to-end. {#reflect |
| me .unnumbered} | rom-raw-material-to-fin | s-production-efficiency- |
|                 | ished-part .unnumbered} | end-to-end. .unnumbered} |
+-----------------+-------------------------+--------------------------+
| ##              | ### Parts               | ###                      |
| # Work-In-Progr |  currently in productio | Helps manage flow and ca |
| ess (WIP) {#wor | n {#parts-currently-in- | pacity planning. {#helps |
| k-in-progress-w | production .unnumbered} | -manage-flow-and-capacit |
| ip .unnumbered} |                         | y-planning. .unnumbered} |
+-----------------+-------------------------+--------------------------+

###  4. Cost & Business Impact Indicators {#cost-business-impact-indicators .unnumbered}

### Link machine data to financial outcomes. {#link-machine-data-to-financial-outcomes. .unnumbered}

+----------------------+---------------------+-------------------------+
| ### KPI              | ### F               | ### Why It'             |
| {#kpi-3 .unnumbered} | ormula / Descriptio | s Important {#why-its-i |
|                      | n {#formula-descrip | mportant-3 .unnumbered} |
|                      | tion-3 .unnumbered} |                         |
+======================+=====================+=========================+
| ###                  | ### (Total operati  | ### Show                |
| Cost per Unit Produc | ng cost / Units pro | s efficiency improvemen |
| ed {#cost-per-unit-p | duced) {#total-oper | ts over time. {#shows-e |
| roduced .unnumbered} | ating-cost-units-pr | fficiency-improvements- |
|                      | oduced .unnumbered} | over-time. .unnumbered} |
+----------------------+---------------------+-------------------------+
| ### Energy Cost per  | ### (Energy consu   | ### Important for sust  |
| Hour / per Part {#en | med × cost rate) {# | ainability and profitab |
| ergy-cost-per-hour-p | energy-consumed-cos | ility. {#important-for- |
| er-part .unnumbered} | t-rate .unnumbered} | sustainability-and-prof |
|                      |                     | itability. .unnumbered} |
+----------------------+---------------------+-------------------------+
| ### Ma               | ### (P              | ### Evaluates capi      |
| chine Return on Inve | rofit generated / M | tal efficiency of each  |
| stment (ROI) {#machi | achine cost) {#prof | machine. {#evaluates-ca |
| ne-return-on-investm | it-generated-machin | pital-efficiency-of-eac |
| ent-roi .unnumbered} | e-cost .unnumbered} | h-machine. .unnumbered} |
+----------------------+---------------------+-------------------------+

###  5. Maintenance & Reliability Indicators {#maintenance-reliability-indicators .unnumbered}

### Especially relevant for CNC and multiaxis systems. {#especially-relevant-for-cnc-and-multiaxis-systems. .unnumbered}

+--------------------+-------------------------+----------------------+
| ### KPI {#         | ### Formula / De        | ### Why It's Impo    |
| kpi-4 .unnumbered} | scription {#formula-des | rtant {#why-its-impo |
|                    | cription-4 .unnumbered} | rtant-4 .unnumbered} |
+====================+=========================+======================+
| ### Mean Tim       | ### Tota                | ##                   |
| e Between Failures | l operating time / Numb | # Measures reliabili |
|  (MTBF) {#mean-tim | er of failures {#total- | ty. {#measures-relia |
| e-between-failures | operating-time-number-o | bility. .unnumbered} |
| -mtbf .unnumbered} | f-failures .unnumbered} |                      |
+--------------------+-------------------------+----------------------+
| ### Mean Time to   | ### Total repair time / | ### Measur           |
|  Repair (MTTR) {#m |  Number of repairs {#to | es maintainability.  |
| ean-time-to-repair | tal-repair-time-number- | {#measures-maintaina |
| -mttr .unnumbered} | of-repairs .unnumbered} | bility. .unnumbered} |
+--------------------+-------------------------+----------------------+
| ### Preventive     | #                       | ###                  |
|  Maintenance Compl | ## (Completed maintenan | Ensures machines are |
| iance {#preventive | ce / Planned maintenanc |  serviced on schedul |
| -maintenance-compl | e) × 100 {#completed-ma | e. {#ensures-machine |
| iance .unnumbered} | intenance-planned-maint | s-are-serviced-on-sc |
|                    | enance-100 .unnumbered} | hedule. .unnumbered} |
+--------------------+-------------------------+----------------------+

###   Chat's suggestions  Example Dashboard Metrics {#chats-suggestions-example-dashboard-metrics .unnumbered}

### If you build this in Power BI, Tableau, or watsonx.data, you could include: {#if-you-build-this-in-power-bi-tableau-or-watsonx.data-you-could-include .unnumbered}

### OEE trend over time 

### Utilization by machine or operator 

### Defect rate vs. production volume 

### Energy cost per machine 

### Downtime causes breakdown (planned vs. unplanned)

###  {#section-3 .unnumbered}

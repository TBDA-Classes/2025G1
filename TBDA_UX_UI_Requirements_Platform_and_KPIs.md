# TBDA_UX_UI_Requirements_Platform_and_KPIs

# UX/UI Requirements Specification – CNC Data Analysis Platform

## 1. Objective of the User Interface

The user interface shall transform complex, high-frequency machine data
into comprehensible, actionable information. It supports monitoring,
analysis, and interpretation of machine behavior with focus on
operational states (Running / Idle / Alarm), energy consumption, program
execution, and contextual alerts. The UI must be intuitive, responsive,
and insight-driven.

## 2. Target Users and Usage Context

| **User Group** | **Goals / Tasks** | **Usage Context** |
| --- | --- | --- |
| Machine Operator | Monitor real-time
machine state; detect
alerts. | Shop floor environment;
touch display. |
| Process / Production
Engineer | Analyze energy usage;
review program
duration; optimize
process. | Office or control room. |
| Maintenance Technician | Analyze and trace
alarms; investigate
failures. | Workshop; possible
mobile use. |
| Management / Production
Lead | Get overview of
utilization; review
efficiency KPIs. | Dashboard view in
office. |

## 

## 3. Functional UX/UI Requirements

### 3.1 Dashboard Design

| **Requirement** | **Description** | **Priority** |
| --- | --- | --- |
| Real-time Status | Show current machine
state (Running, Idle,
Alarm) using clear
color coding. | High |
| KPI Widgets | Display key metrics:
runtime, energy use,
alarms, and program
information. | High |
| Interactive Charts | Zoomable time-series
plots with tooltips and
markers. | High |
| Customizable Dashboard | Allow users to add,
move, or remove
widgets. | Medium |
| Machine Overview (Fleet
View) | Show status and energy
consumption of multiple
machines. | Medium |
| Dark/Light Mode | Adaptable to
environment (shop floor
vs. office). | Low |

### 

### 3.2 Data Analysis View

| **Requirement** | **Description** | **Priority** |
| --- | --- | --- |
| Timeline Visualization | Display machine
operation periods as
colored bands (Running,
Idle, Alarm). | High |
| Program-based Analysis | Filter and visualize
data by program name. | High |
| Energy Analysis | Show energy consumption
per program or time
frame. | High |
| Comparison View | Compare performance,
energy, or duration
across programs or
periods. | Medium |
| Drill-down Function | Clicking data points
opens detailed analysis
(parameters, alarms,
time). | High |
| Export Function | Export charts or tables
(PNG, CSV, PDF). | Medium |

### 

### 3.3 Alarm and Event Management

| **Requirement** | **Description** | **Priority** |
| --- | --- | --- |
| Alarm Overview | List of active and past
alarms with time,
machine, and cause. | High |
| Alarm Context View | Show alarms within the
timeline and correlate
with machine status. | High |
| Filtering & Sorting | Filter by type, time
range, or severity. | Medium |
| Acknowledge & Comment | Allow operators to
acknowledge and add
comments to alarms. | Medium |
| Contextual Hints | Provide insights like
'Alarm occurred during
Tool Change'. | High |

### Concrete performance metrics 1. Machine Performance Indicators (Operational Efficiency)

### These measure how well the CNC or 5-axis machines are running.

| **KPI**  | **Formula / Description**
 | **Why It’s Important**  |
| --- | --- | --- |
| **Mach**ine Utilization
Rate | **(Active mach**
ining time / Tota
l available time)
× 100  | **Shows how much the machines**
are actually used. Low utiliza
tion = underused equipment or
downtime.  |
| **Overall Equip**
ment Effectiven
ess (OEE) | Availability × Performance × Quality  | **Global measure combi**
ning uptime, speed, and qualit
y — a key manufacturing KPI. |
| **Downtime Rat**
e  | **(Downtime hour**s / Total hours)
× 100  | **Identifies mai**
ntenance or setup issues reduc
ing production.  |
| **Cycle**
Time | **Average ti**me to complete on
e machining operation  | **Helps evaluate** efficiency and compare machines or programs.  |
| **Spi**
ndle Load / Power Consumption | **R**eal-time sensor data (if available
) | **Detect**
s overloads, inefficiencies, or maintenance needs.  |

### 2. Production Quality Indicators

### These connect machine precision to output quality.

| **KPI**  | **Formula / Description**  | **Why It’s Important**  |
| --- | --- | --- |
| **Scrap Rate /**
Rejection Rate  | **(Number of defecti**ve parts / Total parts produced) × 100 | **Tracks waste a**
nd cost of rework.  |
| **Rework Rat**e  | **(Parts** requiring re-machining /
Total parts) × 100 | **Meas**ures process stability
.  |
| **Fi**rst Pass Yield
(FPY)  | **(Goo**d parts at first attempt /
Total parts) × 100 | **In**dicates process capabi
lity and setup accuracy.  |

## 3. Production & Throughput Indicators

### Measure overall manufacturing output and bottlenecks.

| **KPI**  | **Formula / De**scription  | **Why I**t’s Important |
| --- | --- | --- |
| **Produ**ction Volume  | **Number of parts prod**uced per day/week  | **Tracks out**put trends. |
| **T**hroughput Time
 | **Ti**me from raw material to
finished part  | **Refl**ects production efficien
cy end-to-end.  |
| **Work-In-Progr**ess (WIP)  | **Parts** currently in production  | Helps manage flow and ca
pacity planning.  |

### 4. Cost & Business Impact Indicators

### Link machine data to financial outcomes.

| **KPI**
 | **Formula / Description**  | **Why It’s Important** |
| --- | --- | --- |
| Cost per Unit Produced  | **(Total operating cost / Units produced)**  | **Shows efficiency improvements over time.**  |
| **Energy Cost per Hour / per Part**  | **(Energy consumed × cost rate)**  | **Important for sustainability and profitability.**  |
| **Machine Return on Investment (ROI)**  | **(Profit generated / Machine cost)**  | **Evaluates capital efficiency of each machine.** |

### 5. Maintenance & Reliability Indicators

### Especially relevant for CNC and multiaxis systems.

| **KPI**  | **Formula / De**scription  | **Why It’s Impo**rtant  |
| --- | --- | --- |
| **Mean Tim**e Between Failures
(MTBF) | **Tota**l operating time / Numb
er of failures | **Measures reliabili**ty.  |
| **Mean Time to** Repair (MTTR)  | **Total repair time /**
Number of repairs  | **Measur**es maintainability.
 |
| **Preventive**
Maintenance Compliance  | **(Completed maintenan**ce / Planned maintenance) × 100  | Ensures machines are
serviced on schedule. |

### Chat’s suggestions Example Dashboard Metrics

### If you build this in Power BI, Tableau, or watsonx.data, you could include:

### OEE trend over time

### Utilization by machine or operator

### Defect rate vs. production volume

### Energy cost per machine

### Downtime causes breakdown (planned vs. unplanned)

###

---
name: engineering-support
description: "Expert electrical and mechanical engineering support. Use this skill whenever the user needs: load calculations, cable sizing, power system design, HVAC/thermal design, pump/piping analysis, specifications, feasibility studies, standards compliance (IEC/EN/NFPA/ΕΛΟΤ), cost estimation, troubleshooting electrical/mechanical systems, solar/renewable design, backup power systems, or infrastructure design. Triggers include: 'calculate demand load', 'size cable', 'design solar system', 'thermal analysis', 'HVAC design', 'specification', 'feasibility study', 'standards compliance', 'what's wrong with this circuit', 'cost estimate', 'energy audit', 'UPS design', 'battery storage', 'power factor correction', 'fault analysis', or any request for structural engineering calculations, equipment selection, or infrastructure design. Also triggers when users reference technical standards (IEC 60364, EN 50160, NFPA, ΕΛΟΤ) or need to interpret engineering requirements."
---

# Engineering Technical Support

Expert-level skill for electrical, mechanical, and infrastructure engineers. Covers calculations, design, documentation, standards compliance, troubleshooting, and cost estimation.

---

## QUICK REFERENCE

**Use this skill for:**

- **Calculations**: Load analysis, cable sizing, power factor correction, thermal load, fault levels, pump sizing, pressure drop
- **Design**: Power distribution, HVAC systems, fire suppression, renewable energy, UPS/backup power, building infrastructure
- **Documentation**: Specifications, feasibility studies, energy audits, condition assessments, as-built documentation, compliance audits
- **Standards**: IEC 60364, EN 50160, NFPA, IEEE, ΕΛΟΤ (Greek)
- **Troubleshooting**: Electrical faults, overheating, system failures, performance issues, root cause analysis
- **Estimation**: Material takeoff, labor hours, lifecycle cost, procurement timeline, energy consumption

---

## CORE WORKFLOWS

### 1. DEMAND & LOAD CALCULATIONS

**When to use**: Building electrical load analysis, peak demand forecasting, system capacity planning

**Outputs:**
- Demand calculations with diversification factors (IEC 60364, IEEE 141)
- Load profiles and growth projections
- Design criteria and safety factors stated explicitly
- Transparent formulas and assumptions

**Example triggers:**
- "Calculate total demand load for a 5,000 m² office (lighting, HVAC, equipment)"
- "What's the peak load for a 200-bed hospital with 5 operating rooms?"
- "Estimate annual energy consumption for a facility with 800 kW connected load"

---

### 2. ELECTRICAL POWER SYSTEMS

**When to use**: Power distribution design, cable sizing, protection coordination, fault analysis

**Includes:**
- **Cable sizing**: Current capacity, voltage drop (IEC 60364, EN 50500), feeder design, cost optimization
- **Voltage drop**: Acceptable limits (typically 3% main, 5% branch), compliance verification
- **Power factor correction**: Reactive power, capacitor sizing, harmonic distortion, cost analysis
- **Short-circuit analysis**: Fault levels, breaker ratings, protection selectivity (IEC 61363)
- **Grounding & earthing**: Resistance calculation, fault current distribution, safety (IEC 60364)
- **UPS/backup power**: Battery sizing, runtime calculations, generator capacity, load shedding

**Example triggers:**
- "Size the main feeder cable from transformer to distribution panel (1.2 MVA, 300 m run)"
- "What breaker rating do I need for 500 A fault level?"
- "Design a backup power system for a hospital (2-hour battery + generator)"

---

### 3. THERMAL & HVAC SYSTEMS

**When to use**: Cooling/heating load analysis, system sizing, energy efficiency, renewable integration

**Includes:**
- **Heat load calculation**: Sensible/latent cooling, solar gain, occupancy, infiltration, seasonal analysis
- **HVAC design**: Unit selection, ductwork sizing, pressure drop, fan power, controls
- **Energy analysis**: Annual kWh consumption, peak demand, operating cost, efficiency improvements
- **Thermal expansion & loss**: Pipe insulation, heat loss, equipment cooling, efficiency margins
- **Solar & renewable**: PV array sizing, battery storage capacity, hybrid systems, grid impact

**Example triggers:**
- "Size a 100 kW solar PV system with 50 kWh battery for a facility"
- "Calculate cooling load for a 10-story office (2 MW total)"
- "How much insulation do I need to reduce heat loss by 20%?"

---

### 4. MECHANICAL SYSTEMS & HYDRAULICS

**When to use**: Pump sizing, piping design, flow/pressure analysis, mechanical infrastructure

**Includes:**
- **Pump sizing**: Flow (m³/h), pressure (bar), power (kW), efficiency, motor selection
- **Piping design**: Friction loss, pressure drop, material selection, velocity limits
- **Fluid mechanics**: Flow rates, pressure requirements, component sizing
- **Thermal expansion**: Pipe/duct movement allowances, safety margins

**Example triggers:**
- "Size a pump for a chilled water system: 50 m³/h, 500 m pipe run, 5 bar"
- "What pipe diameter for 80 m³/h low-temperature chilled water?"

---

### 5. COST ESTIMATION & BOM

**When to use**: Project budgeting, material takeoff, labor estimation, lifecycle costing

**Outputs:**
- Material quantities and unit prices (structured BOM)
- Labor hours with installation/testing/commissioning breakdown
- Procurement timeline with lead times
- Lifecycle cost (initial + operation + maintenance over design life)
- Cost sensitivity analysis for value engineering

**Example triggers:**
- "Create a cost estimate for a 500 kW solar installation (materials, labor, timeline)"
- "What's the material takeoff for a 630 kVA substation?"
- "Calculate the 20-year lifecycle cost vs. initial cost"

---

## TECHNICAL DOCUMENTATION

### Specification Writing

**When to use**: RFQ specs, procurement documents, compliance documentation

**Deliverables:**
- Equipment grades and performance standards
- Testing and commissioning requirements
- Direct standard citations (IEC, EN, NFPA, ΕΛΟΤ)
- Numbered clauses and compliance matrices
- docx/pdf ready format

**Example triggers:**
- "Write a technical specification for a 630 kVA transformer"
- "Draft electrical specifications for a 5 MW substation (IEC 61936)"

---

### Study Reports & Audits

**When to use**: Feasibility analysis, energy audits, condition assessment, compliance audit

**Deliverables:**
- Technical/economic assessment with options comparison
- Energy baseline and efficiency opportunities (kWh, cost, ROI)
- Equipment age and reliability assessment
- Standards gap analysis and corrective action plan
- Professional report format with recommendations

**Example triggers:**
- "Feasibility study: upgrade from diesel generator to solar + battery"
- "Energy audit for a 50,000 m² office complex"
- "Compliance audit against IEC 60364 for this LV system"

---

### Engineer's Documentation

**When to use**: As-built records, calculation sheets, design notebooks

**Deliverables:**
- Structured calculation sheets (markdown or Excel with formulas)
- Design rationale and alternatives considered
- As-built quantities and deviations from design
- Equipment lists with model numbers and spare parts
- Maintenance schedules and procedures

---

## STANDARDS & COMPLIANCE

**Primary standards covered:**

| Domain | Standards |
|--------|-----------|
| **Electrical Safety** | IEC 60364 (LV), IEC 61936 (MV), EN 50160 (power quality) |
| **Cables & Conductors** | EN 50500, IEC 60227, IEC 61089 (current capacity) |
| **Protection & Control** | IEC 61363 (switchgear), IEC 62040 (UPS), IEC 60898 (breakers) |
| **EMC & PQ** | IEC 61000 series, EN 50160, IEC 61800 (drives) |
| **Greece/EU** | ΕΛΟΤ 1425 (LV), ΕΛΟΤ HD 60364, ΤΕΕ guidelines, EU 2014/30/EU, 2014/35/EU |
| **International** | NFPA 70 (NEC), IEEE 141, IEEE 242, ANSI C37 |

**For compliance work:**
- Gap analysis against current standards
- Corrective action plan with prioritization
- Compliance certificates and test report templates

**Example triggers:**
- "Check our office lighting design against ΕΛΟΤ standards"
- "Interpret IEC 60364 requirements for MV switchgear selection"
- "What grounding/bonding is required per IEC 60364-5-54?"

---

## TROUBLESHOOTING & ROOT CAUSE ANALYSIS

**When to use**: System failures, unexpected behavior, performance issues, capacity problems

**Approach:**
1. **Symptom → Root cause**: Structured diagnostic process
2. **Data interpretation**: Power quality data, thermal imaging, vibration analysis, load profiles
3. **Analysis output**: Root cause, affected equipment, severity, remediation steps

**Example triggers:**
- "Why is the main feeder tripping on overload? Analyze this circuit"
- "We have voltage fluctuations in Building B — what's the cause?"
- "Equipment keeps overheating — where should I look?"
- "Can this UPS handle the 30-minute runtime requirement?"

---

## CALCULATION METHODOLOGY

**Every calculation includes:**

1. **Assumptions stated**: Design criteria, standards applied, safety factors, site conditions
2. **Formulas shown**: Transparent math, easy to verify, unit conversions explicit
3. **Results with units**: Clear output, confidence ranges where applicable
4. **Alternatives offered**: Multiple solutions compared with trade-offs

**Standards selection:** Context-aware (Greek/EU/international per location)

---

## KEY FEATURES

✓ **Transparent methodology**: All assumptions, formulas, and intermediate steps shown  
✓ **Standards-aligned**: Direct IEC/EN/NFPA/ΕΛΟΤ citations with plain-language interpretation  
✓ **Professional output**: Specification-ready, audit-trail documentation  
✓ **Handoff-ready**: Complete, reviewable deliverables suitable for PE stamp  
✓ **Trade-off analysis**: When multiple solutions exist, compare costs, risks, performance  
✓ **Site-specific**: Accommodates soil conditions, climate, existing infrastructure, growth projections  

---

## LIMITATIONS & DISCLAIMERS

⚠️ **Licensed PE review required**: Final designs must be reviewed/stamped by licensed professional engineer in jurisdiction  
⚠️ **Field verification needed**: Site-specific conditions (soil resistivity, climate, existing systems) require on-site assessment  
⚠️ **Specialized software**: Complex simulations (CFD, transient analysis, load flow) require dedicated software  
⚠️ **Regulatory authority**: This skill interprets standards; final compliance authority is the local AHJ (authority having jurisdiction)  

---

## QUICK TRIGGER CHECKLIST

Use this skill if you're:

- [ ] Calculating electrical load, power factor, cable size, fault level
- [ ] Sizing HVAC, pump, pipe, solar system, battery storage, UPS
- [ ] Designing electrical distribution, power backup, renewable integration
- [ ] Writing specification, feasibility study, energy audit, compliance report
- [ ] Interpreting IEC, EN, NFPA, ΕΛΟΤ, IEEE standards
- [ ] Troubleshooting electrical or mechanical system failure
- [ ] Estimating cost, material takeoff, labor, lifecycle expense
- [ ] Analyzing power quality, energy consumption, equipment reliability

→ **If any apply, consult this skill.**

---

## FOR MORE DETAILS

Complex topics are documented separately. Ask Claude to reference:

- **Power System Design Details**: Cable sizing, voltage drop, fault analysis, grounding
- **HVAC & Thermal Analysis**: Load calculation, system efficiency, renewable integration
- **Standards Reference**: IEC 60364 sections, EN 50160 compliance, NFPA interpretation
- **Cost Estimation Methods**: Material takeoff, labor hours, lifecycle cost formulas

# GDPR Compliance Framework
# LexGPT Reference — Data protection law, DPA templates, compliance checklist

---

## GDPR Fundamentals

### Key Definitions

**Personal Data:** Any information relating to an identified or identifiable natural person.
Includes: name, email, IP address, location data, cookie identifiers, biometric data.

**Processing:** Any operation performed on personal data — collection, storage,
use, disclosure, erasure.

**Controller:** Determines the purposes and means of processing.
**Processor:** Processes data on behalf of the controller.
**Joint Controllers:** Two or more controllers determining purposes jointly.

**Data Subject:** The natural person whose data is being processed.

---

## The 6 Lawful Bases for Processing

Processing is only lawful if it rests on one of these bases:

| Basis | When to use | Key condition |
|---|---|---|
| Consent | Optional processing, marketing | Freely given, specific, informed, unambiguous |
| Contract | Processing necessary to perform a contract | Data subject is the contracting party |
| Legal obligation | Compliance with EU/national law | Specific legal requirement exists |
| Vital interests | Life-or-death situations | Only when other bases impossible |
| Public task | Public authority functions | Official authority conferred by law |
| Legitimate interests | Business interests balanced against data subject rights | Balancing test required — document it |

**Consent requirements (high standard):**
- Must be freely given (no imbalance of power, no bundling with service)
- Specific to purpose
- Informed (what data, why, by whom)
- Unambiguous (clear affirmative action — no pre-ticked boxes)
- Withdrawable at any time
- Records of consent must be kept

**Legitimate interests:** Most flexible basis but requires documented balancing test.
Three-part test: (1) legitimate interest exists, (2) processing is necessary,
(3) individual's interests don't override.

---

## The 8 Data Subject Rights

Every privacy policy must explain these rights. Every system must support them.

| Right | What it means | Response time |
|---|---|---|
| Right of access (Article 15) | Copy of data + processing information | 1 month |
| Right to rectification (Article 16) | Correct inaccurate data | 1 month |
| Right to erasure (Article 17) | "Right to be forgotten" — delete data | 1 month |
| Right to restriction (Article 18) | Pause processing while dispute resolved | 1 month |
| Right to data portability (Article 20) | Receive data in machine-readable format | 1 month |
| Right to object (Article 21) | Object to legitimate interest processing | Immediately |
| Rights re: automated decisions (Article 22) | Not subject to solely automated decisions | Case by case |
| Right to withdraw consent | Withdraw previously given consent | Immediately |

**Response time:** 1 month standard, extendable by 2 months for complex requests
(must notify data subject of extension within 1 month).

---

## Data Processing Agreement (DPA) Template

A DPA is required when a controller engages a processor.
This is a required document under GDPR Article 28.

```
DATA PROCESSING AGREEMENT

This Data Processing Agreement ("DPA") forms part of the agreement between 
[Controller name] ("Controller") and [Processor name] ("Processor").

1. DEFINITIONS
   Terms defined in GDPR (EU 2016/679) have the same meaning here.

2. PROCESSING DETAILS
   Subject matter: [Description of processing]
   Duration: [Term of main agreement]
   Nature and purpose: [Specific processing activities]
   Type of personal data: [Categories of data]
   Categories of data subjects: [Who the data relates to]

3. PROCESSOR OBLIGATIONS
   The Processor shall:
   (a) Process personal data only on documented instructions from the Controller;
   (b) Ensure authorised persons are bound by confidentiality;
   (c) Implement appropriate technical and organisational security measures 
       (Article 32);
   (d) Not engage sub-processors without prior written authorisation;
   (e) Assist the Controller with data subject rights requests;
   (f) Assist the Controller with security obligations (Articles 32-36);
   (g) Delete or return all personal data on termination;
   (h) Make available all information necessary to demonstrate compliance;
   (i) Allow and contribute to audits by the Controller.

4. SUB-PROCESSORS
   The Processor may engage sub-processors only with prior written consent.
   The Processor shall impose equivalent obligations on sub-processors.
   Current sub-processors: [List or reference to maintained list]

5. INTERNATIONAL TRANSFERS
   No personal data shall be transferred outside the EEA without:
   (a) An adequacy decision; or
   (b) Standard Contractual Clauses (SCCs); or
   (c) Another lawful transfer mechanism.

6. SECURITY MEASURES
   The Processor shall implement at minimum:
   - Encryption of personal data at rest and in transit
   - Ongoing confidentiality, integrity, availability of systems
   - Ability to restore data following incident
   - Regular testing of security measures

7. DATA BREACH NOTIFICATION
   The Processor shall notify the Controller without undue delay 
   (and within 72 hours where feasible) upon becoming aware of a 
   personal data breach.

8. CONTROLLER INSTRUCTIONS
   The Controller's current processing instructions are set out in 
   Schedule 1 to this DPA.
```

---

## Privacy Policy — Required Elements

A GDPR-compliant privacy policy must include:

**Identity of controller:**
Full legal name, address, registration number, contact details.

**DPO contact (if applicable):**
Data Protection Officer name and contact details.

**Purposes and legal basis:**
For each processing activity: what data, why, on what legal basis.

**Recipients:**
Who receives the data (categories of recipients, specific names where possible).

**International transfers:**
If data leaves the EEA: which countries, what safeguards.

**Retention periods:**
How long data is kept for each purpose.

**Data subject rights:**
All 8 rights listed with how to exercise them.

**Right to complain:**
Contact details of supervisory authority (Hellenic DPA: www.dpa.gr).

**Automated decision-making:**
If used: logic involved, significance, and consequences.

**Updates:**
When and how the policy may be updated.

---

## GDPR Compliance Checklist

### For any organisation handling personal data:

**Governance:**
- [ ] Data Protection Officer appointed (if required)
- [ ] Records of Processing Activities (ROPA) maintained
- [ ] Privacy policy published and accessible
- [ ] Cookie consent mechanism implemented (where applicable)
- [ ] Data retention policy defined and implemented

**Contracts:**
- [ ] DPAs in place with all processors
- [ ] Sub-processor lists maintained
- [ ] Standard Contractual Clauses for international transfers

**Rights:**
- [ ] Process for handling data subject requests
- [ ] Response time tracking (1 month deadline)
- [ ] Identity verification process for requests

**Security:**
- [ ] Technical and organisational measures documented
- [ ] Data breach response procedure in place
- [ ] 72-hour notification process to supervisory authority

**Hellenic DPA (ΑΠΔΠΧ) specifics:**
- Registration not generally required for most controllers
- Specific activities may require prior consultation
- Breach notification: www.dpa.gr
- Complaint handling: www.dpa.gr

---

## EU AI Act — Key Compliance Requirements

### Risk Categories

**Unacceptable risk (prohibited):**
Social scoring by governments, real-time biometric surveillance in public spaces,
manipulation of vulnerable groups, subliminal techniques.

**High risk (significant obligations):**
AI in critical infrastructure, educational decisions, employment decisions,
essential services, law enforcement, migration, justice administration.

**Limited risk (transparency obligations):**
Chatbots must disclose they are AI. Deepfakes must be labelled.

**Minimal risk:**
AI in spam filters, video games — no specific obligations.

**High-risk AI obligations include:**
- Risk management system
- Data governance and management
- Technical documentation
- Logging and traceability
- Transparency and information to users
- Human oversight measures
- Accuracy, robustness, and cybersecurity

**Timeline:**
- Prohibited uses: February 2025
- High-risk (Annex I): August 2026
- High-risk (Annex III): August 2027

[LEGAL REVIEW REQUIRED] for any AI system that may be high-risk under the Act.

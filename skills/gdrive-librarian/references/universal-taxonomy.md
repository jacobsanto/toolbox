# Universal Folder Taxonomy — Reference

Use this file during Phase 1 Step 3 to propose an adapted taxonomy.
Pick the closest business type and customise based on the onboarding interview.

---

## 1. Hospitality (Hotels, Villas, Short-Term Rentals)

```
01_Guest_Relations/        [RESTRICTED — PII]
  ├── Booking_Agreements/
  ├── Guest_IDs/
  └── Concierge_Requests/
02_Marketing_Assets/
  ├── Photography/
  ├── Drone_Footage/
  └── Social_Media_Templates/
03_Property_Operations/
  ├── [PropertyName]/
  │   ├── Maintenance_Logs/
  │   ├── Manuals/
  │   └── Schedules/
04_Finance/                [RESTRICTED]
  ├── Invoices/
  ├── Vendor_Contracts/
  └── Tax/
05_HR/                     [RESTRICTED]
  ├── Contracts/
  └── Payroll/
```

---

## 2. Legal Firm

```
01_Client_Files/           [RESTRICTED — PII]
  ├── [ClientName]/
  │   ├── Correspondence/
  │   ├── Court_Documents/
  │   └── Contracts/
02_Internal_Operations/
  ├── Templates/
  ├── Research/
  └── Precedents/
03_Finance/                [RESTRICTED]
  ├── Invoices/
  ├── Billing/
  └── Tax/
04_HR/                     [RESTRICTED]
  ├── Contracts/
  └── Training/
05_Marketing/
  ├── Website_Assets/
  └── Publications/
```

---

## 3. Creative / Marketing Agency

```
01_Client_Projects/
  ├── [ClientName]/
  │   ├── Briefs/
  │   ├── Assets/
  │   ├── Deliverables/
  │   └── Approvals/
02_Internal_Assets/
  ├── Brand_Guidelines/
  ├── Templates/
  └── Stock_Media/
03_Finance/                [RESTRICTED]
  ├── Invoices/
  ├── Proposals/
  └── Tax/
04_HR/                     [RESTRICTED]
  ├── Contracts/
  └── Freelancers/
05_Operations/
  ├── Tools_Licences/
  └── Processes/
```

---

## 4. E-Commerce / Retail

```
01_Products/
  ├── [Category]/
  │   ├── Photos/
  │   └── Spec_Sheets/
02_Suppliers/
  ├── [SupplierName]/
  │   ├── Contracts/
  │   ├── Invoices/
  │   └── Correspondence/
03_Marketing/
  ├── Campaigns/
  ├── Social_Assets/
  └── Email_Templates/
04_Finance/                [RESTRICTED]
  ├── Invoices/
  ├── Expenses/
  └── Tax/
05_Operations/
  ├── Logistics/
  ├── Returns/
  └── SOPs/
```

---

## 5. Healthcare / Medical Practice

```
01_Patient_Records/        [RESTRICTED — PII / Medical]
  ├── [PatientID]/
02_Clinical_Operations/
  ├── Protocols/
  ├── Equipment_Manuals/
  └── Schedules/
03_Compliance/             [RESTRICTED]
  ├── Licences/
  ├── Audits/
  └── Insurance/
04_Finance/                [RESTRICTED]
  ├── Invoices/
  ├── Insurance_Claims/
  └── Tax/
05_HR/                     [RESTRICTED]
  ├── Staff_Contracts/
  └── Training_Certifications/
06_Marketing/
  ├── Website_Assets/
  └── Patient_Communications/
```

---

## 6. Real Estate Agency

```
01_Properties/
  ├── [PropertyID_Address]/
  │   ├── Photos/
  │   ├── Floor_Plans/
  │   ├── Legal_Docs/       [RESTRICTED]
  │   └── Valuation_Reports/
02_Clients/                [RESTRICTED — PII]
  ├── Buyers/
  └── Sellers/
03_Finance/                [RESTRICTED]
  ├── Commission_Records/
  ├── Invoices/
  └── Tax/
04_Marketing/
  ├── Listings/
  ├── Social_Assets/
  └── Campaign_Materials/
05_Operations/
  ├── Templates/
  ├── Legal_Frameworks/
  └── Partner_Agreements/
```

---

## 7. Consulting Firm

```
01_Engagements/
  ├── [ClientName_ProjectName]/
  │   ├── Discovery/
  │   ├── Deliverables/
  │   ├── Presentations/
  │   └── Contracts/        [RESTRICTED]
02_Knowledge_Base/
  ├── Frameworks/
  ├── Case_Studies/
  └── Research/
03_Finance/                [RESTRICTED]
  ├── Proposals/
  ├── Invoices/
  └── Tax/
04_HR/                     [RESTRICTED]
  ├── Consultant_Contracts/
  └── Performance_Reviews/
05_Marketing/
  ├── Credentials/
  ├── Thought_Leadership/
  └── Website_Assets/
```

---

## 8. NGO / Non-Profit

```
01_Programmes/
  ├── [ProgrammeName]/
  │   ├── Reports/
  │   ├── Beneficiary_Data/  [RESTRICTED — PII]
  │   └── Field_Materials/
02_Fundraising/
  ├── Grant_Applications/
  ├── Donor_Records/         [RESTRICTED]
  └── Campaign_Assets/
03_Finance/                  [RESTRICTED]
  ├── Budgets/
  ├── Invoices/
  └── Audit_Reports/
04_HR/                       [RESTRICTED]
  ├── Staff_Contracts/
  └── Volunteer_Records/
05_Communications/
  ├── Press_Releases/
  ├── Social_Assets/
  └── Annual_Reports/
```

---

## 9. Tech / SaaS Company

```
01_Product/
  ├── Specs/
  ├── Design_Assets/
  └── Release_Notes/
02_Engineering/
  ├── Architecture_Docs/
  ├── Runbooks/
  └── Security/              [RESTRICTED]
03_Sales_Marketing/
  ├── Pitch_Decks/
  ├── Case_Studies/
  └── Brand_Assets/
04_Finance/                  [RESTRICTED]
  ├── Invoices/
  ├── Investor_Docs/
  └── Tax/
05_HR/                       [RESTRICTED]
  ├── Contracts/
  ├── Equity_Docs/
  └── Onboarding/
06_Legal/                    [RESTRICTED]
  ├── IP/
  ├── Vendor_Agreements/
  └── Privacy_Compliance/
```

---

## 10. General / Multi-Sector (Default Fallback)

Use when business type is unclear or spans multiple sectors.

```
01_Finance/                [RESTRICTED]
  ├── Invoices/
  ├── Contracts/
  └── Tax/
02_Operations/
  ├── Processes/
  ├── Manuals/
  └── Schedules/
03_People/                 [RESTRICTED — PII]
  ├── Contracts/
  ├── IDs/
  └── Payroll/
04_Marketing/
  ├── Brand_Assets/
  ├── Campaigns/
  └── Content/
05_Legal/                  [RESTRICTED]
  ├── Agreements/
  └── Compliance/
06_Archive/
  └── [YYYY]/
```

---

## Naming Convention (Universal)

```
YYYY-MM-DD_[Category]_[Entity]_[BriefDescription].[ext]
```

| Token | Meaning | Example |
|---|---|---|
| YYYY-MM-DD | File date (content date > modified date > today) | 2026-04-24 |
| Category | Document type | Invoice, Contract, Photo, Report |
| Entity | Client, vendor, property, person | AcmeCorp, VillaHelios, JohnDoe |
| BriefDescription | 2–4 word descriptor, underscores | PoolMaintenance, ServiceAgreement |

**Never use spaces. Use underscores. Max filename length: 100 characters.**

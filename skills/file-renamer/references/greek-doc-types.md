# Greek Business Document Types — Naming Taxonomy

## Φορολογικά / Tax Documents

| Document | Greek name | DocType field | ΌνομαΑπόΠεριεχόμενο = | Date = |
|----------|-----------|---------------|----------------------|--------|
| Invoice | Τιμολόγιο Πώλησης | `Τιμολόγιο` | Εκδότης ή αποδέκτης | Ημ. έκδοσης |
| Receipt | Απόδειξη Λιανικής | `Απόδειξη` | Εκδότης | Ημ. έκδοσης |
| Credit note | Πιστωτικό Τιμολόγιο | `Πιστωτικό` | Εκδότης | Ημ. έκδοσης |
| Professional fee receipt | ΑΠΥ | `ΑΠΥ` | Παρέχων υπηρεσίες | Ημ. έκδοσης |
| VAT return | Δήλωση ΦΠΑ | `ΔήλωσηΦΠΑ` | ΑΑΔΕ | Φορολ. περίοδος |
| Income tax return | Φορολογική Δήλωση Ε1 | `Ε1` | ΑΑΔΕ | Έτος χρήσης |
| Business income E3 | Δήλωση Ε3 | `Ε3` | ΑΑΔΕ | Έτος χρήσης |
| Property E9 | Δήλωση Ε9 | `Ε9` | ΑΑΔΕ | Έτος |
| Tax clearance | Φορολογική Ενημερότητα | `Ενημερότητα` | ΑΑΔΕ | Ημ. έκδοσης |
| Payment proof | Αποδεικτικό Πληρωμής | `ΑποδεικτικόΠληρωμής` | ΑΑΔΕ/Τράπεζα | Ημ. πληρωμής |

## Ασφαλιστικά / Social Insurance

| Document | DocType field | Entity = | Date = |
|----------|--------------|---------|--------|
| ΕΦΚΑ insurance certificate | `Βεβαίωση-ΕΦΚΑ` | ΕΦΚΑ | Ημ. έκδοσης |
| Employer declaration APD | `ΑΠΔ` | Εργοδότης | Μήνας ΑΠΔ |
| Insurance clearance | `Ασφαλιστική-Ενημερότητα` | ΕΦΚΑ | Ημ. έκδοσης |
| Employer certificate | `Βεβαίωση-Εργοδότη` | Εργοδότης | Ημ. έκδοσης |
| Payslip | `Μισθοδοσία` | Εταιρεία | Μήνας-Έτος |

## Τραπεζικά / Banking

| Document | DocType field | Entity = | Date = |
|----------|--------------|---------|--------|
| Bank statement | `Κίνηση` | Τράπεζα | Ημ. κατάστασης |
| Transfer confirmation | `Μεταφορά` | Τράπεζα | Ημ. συναλλαγής |
| Loan contract | `Δάνειο` | Τράπεζα | Ημ. υπογραφής |
| Standing order | `ΠάγιαΕντολή` | Τράπεζα | Ημ. ρύθμισης |

## Νομικά / Legal

| Document | DocType field | Entity = | Date = |
|----------|--------------|---------|--------|
| Contract | `Συμβόλαιο` | Αντισυμβαλλόμενοι (A-B) | Ημ. υπογραφής |
| NDA | `NDA` | Αντισυμβαλλόμενοι | Ημ. υπογραφής |
| Court decision | `ΔικαστικήΑπόφαση` | Δικαστήριο | Ημ. απόφασης |
| Notarial deed | `ΣυμβολαιογραφικήΠράξη` | Συμβολαιογράφος | Ημ. πράξης |
| Power of attorney | `Πληρεξούσιο` | Εκδότης | Ημ. έκδοσης |

## Επιχειρηματικά / Business Ops

| Document | DocType field | Entity = | Date = |
|----------|--------------|---------|--------|
| Offer / Quote | `Προσφορά` | Προσφέρων | Ημ. προσφοράς |
| Order | `Παραγγελία` | Παραγγελιοδότης | Ημ. παραγγελίας |
| Delivery note | `ΔελτίοΑποστολής` | Αποστολέας | Ημ. αποστολής |
| Meeting minutes | `Πρακτικό` | Εταιρεία | Ημ. συνεδρίασης |
| Regulation / Policy | `Κανονισμός` | Εκδότης | Ημ. έκδοσης |

## Ακίνητα / Real Estate

| Document | DocType field | Entity = | Date = |
|----------|--------------|---------|--------|
| Lease agreement | `Μίσθωση` | Ιδιοκτήτης-Μισθωτής | Ημ. υπογραφής |
| Property certificate | `Πιστοποιητικό-ΕΝΦΙΑ` | ΑΑΔΕ | Έτος |
| Building permit | `ΟικοδομικήΆδεια` | Δήμος | Ημ. έκδοσης |
| Energy certificate | `ΠΕΑ` | Μηχανικός | Ημ. έκδοσης |

## Ταξιδιωτικά / ID Documents

| Document | DocType field | Entity = | Date = |
|----------|--------------|---------|--------|
| Passport | `Διαβατήριο` | Κάτοχος (ΕΠΩΝΥΜΟ) | Ημ. λήξης |
| National ID | `Ταυτότητα` | Κάτοχος (ΕΠΩΝΥΜΟ) | Ημ. έκδοσης |
| Residence permit | `ΆδειαΔιαμονής` | Κάτοχος | Ημ. λήξης |

## Γενικά / Generic (when type unclear)

| Situation | DocType field |
|-----------|--------------|
| Αλληλογραφία / Email printout | `Επιστολή` |
| Screenshot / proof | `Screenshot` |
| Report / study | `Αναφορά` |
| Presentation | `Παρουσίαση` |
| Scan of unclear purpose | `Σκαν` |
| Technical document | `Τεχνικό` |

## Naming examples (confirmed from live Drive)

```
ΔΑΚΟΥΤΡΟΣ_Ασφαλιστικό_1990-07-15.docx
ΔΑΚΟΥΤΡΟΣ_Βεβαίωση_2024-01-01.docx
ΔΑΚΟΥΤΡΟΣ_Λογαριασμός.docx
ΔΑΚΟΥΤΡΟΣ-ΙΚΕ_ΑΠΔ_2025-03.pdf
ALPHA-SERVICES-AE_Τιμολόγιο_2024-11-07.pdf
ΑΛΕΞΙΟΥ-ΔΑΚΟΥΤΡΟΣ-ΟΕ_Βεβαίωση-ΕΦΚΑ_2025-01.pdf
WIND_Λογαριασμός_2024-12-01.pdf
ARIVIA_Συμβόλαιο_2025-06-01.pdf
WIND_Διαδικασία.6_TechnicalDeployment.docx
```

## Special rules for Arivia/Dakoutros entities

Known entity codes to use consistently:

| Legal name | Entity code in filename |
|-----------|------------------------|
| ΔΑΚΟΥΤΡΟΣ Ι. & Μ. Ε.Ε. | `ΔΑΚΟΥΤΡΟΣ-ΕΕ` |
| ΔΑΚΟΥΤΡΟΣ Ι ΙΚΕ | `ΔΑΚΟΥΤΡΟΣ-ΙΚΕ` |
| ΑΛΕΞΙΟΥ ΔΑΚΟΥΤΡΟΣ ΟΕ | `ΑΛΕΞΙΟΥ-ΔΑΚΟΥΤΡΟΣ-ΟΕ` |
| P.DEVELOPMENT | `P-DEVELOPMENT` |
| VESRANTO | `VESRANTO` |
| Arivia Group | `ARIVIA` |
| Γεν. Νοσοκομείο Θήρας | `ΓΝΘ` |
| ΑΑΔΕ / εφορία | `ΑΑΔΕ` |
| ΕΦΚΑ | `ΕΦΚΑ` |
| Personal (Ιάκωβος Δακουτρός) | `ΔΑΚΟΥΤΡΟΣ` |

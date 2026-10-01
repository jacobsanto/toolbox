const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, LevelFormat, TabStopType,
  TabStopPosition
} = require('docx');
const fs = require('fs');

const COLORS = {
  amber:  'BA7517',
  teal:   '0F6E56',
  purple: '3C3489',
  blue:   '0C447C',
  red:    '791F1F',
  bg1:    'FAEEDA',
  bg2:    'E1F5EE',
  bg3:    'EEEDFE',
  bg4:    'E6F1FB',
  bg5:    'FCEBEB',
  bgsuccess: 'EAF3DE',
  gray:   'F5F5F5',
  darkgray: '444441',
  lightgray: 'E8E8E8',
  white:  'FFFFFF',
  black:  '1A1A1A',
};

const border = { style: BorderStyle.SINGLE, size: 1, color: 'DDDDDD' };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorder = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

function cell(text, opts = {}) {
  const {
    bold = false, color = COLORS.black, bg = COLORS.white,
    size = 20, width = 4680, align = AlignmentType.LEFT,
    italic = false
  } = opts;
  return new TableCell({
    borders: opts.noBorder ? noBorders : borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: bg, type: ShadingType.CLEAR },
    margins: { top: 100, bottom: 100, left: 140, right: 140 },
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      alignment: align,
      children: [new TextRun({ text, bold, color, size, font: 'Arial', italics: italic })]
    })]
  });
}

function heading1(text, color = COLORS.black) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 120 },
    children: [new TextRun({ text, bold: true, size: 36, font: 'Arial', color })]
  });
}

function heading2(text, color = COLORS.darkgray) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 80 },
    children: [new TextRun({ text, bold: true, size: 26, font: 'Arial', color })]
  });
}

function heading3(text, color = COLORS.darkgray) {
  return new Paragraph({
    spacing: { before: 200, after: 60 },
    children: [new TextRun({ text, bold: true, size: 22, font: 'Arial', color })]
  });
}

function body(text, opts = {}) {
  const { bold = false, color = COLORS.black, size = 20, spacing = { after: 80 } } = opts;
  return new Paragraph({
    spacing,
    children: [new TextRun({ text, bold, color, size, font: 'Arial' })]
  });
}

function bullet(text, opts = {}) {
  const { color = COLORS.black, size = 20 } = opts;
  return new Paragraph({
    numbering: { reference: 'bullets', level: 0 },
    spacing: { after: 60 },
    children: [new TextRun({ text, color, size, font: 'Arial' })]
  });
}

function divider(color = COLORS.lightgray) {
  return new Paragraph({
    spacing: { before: 80, after: 80 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color, space: 1 } },
    children: []
  });
}

function phaseHeader(num, title, subtitle, bg, textColor) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [720, 8640],
    rows: [new TableRow({ children: [
      new TableCell({
        borders: noBorders,
        width: { size: 720, type: WidthType.DXA },
        shading: { fill: bg, type: ShadingType.CLEAR },
        margins: { top: 120, bottom: 120, left: 160, right: 160 },
        verticalAlign: VerticalAlign.CENTER,
        children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
          new TextRun({ text: num, bold: true, size: 28, font: 'Arial', color: textColor })
        ]})]
      }),
      new TableCell({
        borders: noBorders,
        width: { size: 8640, type: WidthType.DXA },
        shading: { fill: bg, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 200, right: 160 },
        children: [
          new Paragraph({ spacing: { after: 20 }, children: [
            new TextRun({ text: title, bold: true, size: 26, font: 'Arial', color: textColor })
          ]}),
          new Paragraph({ spacing: { after: 0 }, children: [
            new TextRun({ text: subtitle, size: 18, font: 'Arial', color: textColor, italics: true })
          ]})
        ]
      })
    ]})]
  });
}

function stepTable(steps) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [560, 8800],
    rows: steps.map((s, i) => new TableRow({
      children: [
        new TableCell({
          borders: noBorders,
          width: { size: 560, type: WidthType.DXA },
          shading: { fill: i % 2 === 0 ? COLORS.gray : COLORS.white, type: ShadingType.CLEAR },
          margins: { top: 100, bottom: 100, left: 140, right: 100 },
          verticalAlign: VerticalAlign.TOP,
          children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
            new TextRun({ text: s.id, bold: true, size: 18, font: 'Arial', color: COLORS.darkgray })
          ]})]
        }),
        new TableCell({
          borders: noBorders,
          width: { size: 8800, type: WidthType.DXA },
          shading: { fill: i % 2 === 0 ? COLORS.gray : COLORS.white, type: ShadingType.CLEAR },
          margins: { top: 100, bottom: 100, left: 160, right: 140 },
          children: [
            new Paragraph({ spacing: { after: 30 }, children: [
              new TextRun({ text: s.title, bold: true, size: 21, font: 'Arial', color: COLORS.black })
            ]}),
            new Paragraph({ spacing: { after: 60 }, children: [
              new TextRun({ text: s.desc, size: 19, font: 'Arial', color: COLORS.darkgray })
            ]}),
            new Paragraph({ spacing: { after: 0 }, children: s.tags.map(t =>
              new TextRun({ text: `  ${t}  `, size: 16, font: 'Arial',
                color: t.includes('€') ? COLORS.amber : t.includes('Αγορά') ? COLORS.red :
                       t.includes('Έχεις') ? COLORS.teal : COLORS.blue,
                bold: true
              })
            )})
          ]
        })
      ]
    }))
  });
}

function summaryTable() {
  const items = [
    { num: '~235€', label: 'Υποχρεωτικές αγορές', sub: 'Αεροσυμπιεστής + πυροσβεστήρας' },
    { num: '~900€', label: 'Υποδομές + πάγκοι', sub: 'Ρεύμα, φως, ράφια, ξύλα' },
    { num: '~1.135€', label: 'Σύνολο (εκτίμηση)', sub: 'Χωρίς εργατικά ηλεκτρολόγου' },
  ];
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [3120, 3120, 3120],
    rows: [new TableRow({ children: items.map(it =>
      new TableCell({
        borders,
        width: { size: 3120, type: WidthType.DXA },
        shading: { fill: COLORS.bgsuccess, type: ShadingType.CLEAR },
        margins: { top: 160, bottom: 160, left: 200, right: 200 },
        verticalAlign: VerticalAlign.CENTER,
        children: [
          new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 }, children: [
            new TextRun({ text: it.num, bold: true, size: 32, font: 'Arial', color: COLORS.teal })
          ]}),
          new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 20 }, children: [
            new TextRun({ text: it.label, bold: true, size: 18, font: 'Arial', color: COLORS.black })
          ]}),
          new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 0 }, children: [
            new TextRun({ text: it.sub, size: 16, font: 'Arial', color: COLORS.darkgray, italics: true })
          ]})
        ]
      })
    )})]
  });
}

const phases = [
  {
    num: '1', title: 'Αδειάσιμο και απογραφή',
    subtitle: 'Εβδομάδα 1–2 · Μηδενικό κόστος',
    bg: COLORS.bg1, textColor: COLORS.amber,
    steps: [
      { id: '1.1', title: 'Βγάλε τα πάντα έξω',
        desc: 'Αδείασε τον χώρο εντελώς — αυτοκίνητο, εργαλεία, κουτιά, όλα. Είναι η μόνη ευκαιρία να δεις το δάπεδο και τους τοίχους καθαρά.',
        tags: ['2 ημέρες'] },
      { id: '1.2', title: 'Καθάρισε και επιθεώρησε',
        desc: 'Σκούπισε, ξέπλυνε δάπεδο. Έλεγξε τοίχους για υγρασία, ρωγμές, κακές πρίζες. Σημείωσε τι χρειάζεται επισκευή πριν μπει ο εξοπλισμός.',
        tags: ['1 ημέρα'] },
      { id: '1.3', title: 'Ταξινόμησε εργαλεία σε 3 σωρούς',
        desc: 'Σωρός Α: κρατάς σίγουρα. Σωρός Β: ίσως/διπλά. Σωρός Γ: πέταμα/δωρεά. Μη βάλεις πίσω τίποτα από τον Γ.',
        tags: ['1 ημέρα'] },
      { id: '1.4', title: 'Φωτογράφισε και καταγραφή απογραφής',
        desc: 'Φωτογράφισε κάθε εργαλείο ξεχωριστά. Ενημέρωσε τη λίστα που φτιάξαμε — θα ξέρεις τι έχεις πριν αγοράσεις κάτι νέο.',
        tags: ['1 ημέρα'] },
    ]
  },
  {
    num: '2', title: 'Υποδομές — ρεύμα, φωτισμός, τοίχοι',
    subtitle: 'Εβδομάδα 2–4 · Σημαντικότερη φάση — κάνε την πρώτη',
    bg: COLORS.bg2, textColor: COLORS.teal,
    steps: [
      { id: '2.1', title: 'Ηλεκτρολογικές παροχές πάνω από τον πάγκο',
        desc: 'Τουλάχιστον 4–6 πρίζες σε ράγα κατά μήκος του πάνω τοίχου. Χωριστή γραμμή 16Α για βαριά εργαλεία (τροχός, δράπανο στήλης). Καλύτερα να το κάνει ηλεκτρολόγος.',
        tags: ['1–2 ημέρες', '~150–300€'] },
      { id: '2.2', title: 'Φωτισμός εργασίας LED πάνω από τον πάγκο',
        desc: 'Γραμμικά LED (4000K–5000K, ψυχρό λευκό) κατά μήκος ολόκληρου του πάνω τοίχου. Στόχος: χωρίς σκιές πάνω στον πάγκο. Ελάχιστο 3000 lumen.',
        tags: ['1 ημέρα', '~80–150€'] },
      { id: '2.3', title: 'Τοποθέτηση perforated panel πάνω από πάγκο',
        desc: 'Στερέωσε το υπάρχον panel σταθερά. Αν χρειάζεται επέκταση, πρόσθεσε νέα φύλλα (1,22×2,44μ ~25–40€/φύλλο). Χρειάζεσαι ~4 φύλλα για 10μ.',
        tags: ['Έχεις ήδη μέρος', '~100–160€ για επέκταση'] },
      { id: '2.4', title: 'Ράφια βαρέως τύπου (κάτω τοίχος)',
        desc: 'Μεταλλικά ράφια βαρέως τύπου σε όλο τον κάτω τοίχο. 4 επίπεδα, 200–300κγ ανά επίπεδο. Στερέωση με μπουλόνια στο δάπεδο ή/και τοίχο.',
        tags: ['1–2 ημέρες', '~200–400€'] },
    ]
  },
  {
    num: '3', title: 'Πάγκοι εργασίας',
    subtitle: 'Εβδομάδα 4–6 · Η καρδιά του εργαστηρίου',
    bg: COLORS.bg3, textColor: COLORS.purple,
    steps: [
      { id: '3.1', title: 'Πάγκος ξύλου (αριστερά, 5μ)',
        desc: 'Βαρύς πάγκος από μασίφ ξύλο ή MDF 40χιλ σε μεταλλικό σκελετό. Ύψος 85–90εκ, βάθος 65εκ. Μέγγενη ξύλου Record/Irwin στα αριστερά. Μπορεί να γίνει DIY.',
        tags: ['1–2 ημέρες κατασκευή', '~150–350€ υλικά'] },
      { id: '3.2', title: 'Πάγκος σιδήρου (δεξιά, 5μ)',
        desc: 'Μεταλλικός σκελετός τετράγωνο σωλήνα 40×40χιλ + επιφάνεια μεταλλικό φύλλο 6–8χιλ. Μέγγενη μετάλλου στα δεξιά. Κοντά στην Πόρτα 2 για αερισμό.',
        tags: ['2–3 ημέρες κατασκευή', '~200–400€ υλικά'] },
      { id: '3.3', title: 'Γάντζοι και αξεσουάρ perforated panel',
        desc: 'Σετ γάντζων διαφόρων μεγεθών. Αριστερά: εργαλεία ξύλου (πριόνια, σφυριά, καλέμια). Δεξιά: εργαλεία σιδήρου (τροχοί, λίμες, κλειδιά).',
        tags: ['1 ημέρα', '~30–60€'] },
    ]
  },
  {
    num: '4', title: 'Οργάνωση αποθήκευσης',
    subtitle: 'Εβδομάδα 6–9 · Κάθε εργαλείο έχει τη θέση του',
    bg: COLORS.bg4, textColor: COLORS.blue,
    steps: [
      { id: '4.1', title: 'Τοποθέτηση τροχήλατου ντουλαπιού',
        desc: 'Ο μαύρος τροχήλατος που έχεις ήδη πάει κάτω/δίπλα στον πάγκο ξύλου. Πάνω συρτάρι → τρυπάνια/μύτες, μέσα → μετρητικά, κάτω → ηλεκτρικά χειρός.',
        tags: ['Έχεις ήδη', '0.5 ημέρα'] },
      { id: '4.2', title: 'Ράφια τοίχου βάθους (εργαλεία χειρός)',
        desc: 'Αριστερά παραθύρου: πριόνια, σφυριά, καλέμια, κλειδιά. Δεξιά παραθύρου: δίσκοι τροχού, μέτρα, αλφάδια, καρφωτικά, κατσαβίδια.',
        tags: ['1 ημέρα', '~60–120€ ράφια'] },
      { id: '4.3', title: 'Οργάνωση κάτω ραφιών ανά κατηγορία',
        desc: 'Ράφι 4 (χαμηλά): αεροσυμπιεστής + shop vac + σκάλα. Ράφι 3: SDS + αναμίκτης + sander. Ράφι 2: βαφή (αριστερά) + οικοδομικά (δεξιά). Ράφι 1 (ψηλά): σπάνια χρήση.',
        tags: ['1 ημέρα'] },
      { id: '4.4', title: 'Ετικέτες και σήμανση',
        desc: 'Βάλε ετικέτες σε κάθε ράφι και συρτάρι. Απλά αυτοκόλλητα με μαρκαδόρο αρκούν. Εξοικονομεί ώρες ψαξίματος αργότερα.',
        tags: ['0.5 ημέρα', '~10€'] },
    ]
  },
  {
    num: '5', title: 'Αγορές που λείπουν + ασφάλεια',
    subtitle: 'Εβδομάδα 9–10 · Υποχρεωτικό πριν τη λειτουργία',
    bg: COLORS.bg5, textColor: COLORS.red,
    steps: [
      { id: '5.1', title: 'Αεροσυμπιεστής',
        desc: 'DeWalt D55153 (24L, 1.5HP, ήσυχος) ή Michelin MB 24. Τοποθέτηση στο χαμηλό ράφι κάτω τοίχου. Quick connect σύνδεσμος για εύκολη χρήση.',
        tags: ['Αγορά', '~180–280€'] },
      { id: '5.2', title: 'Πυροσβεστήρας ξηράς κόνεως 6κγ',
        desc: 'Υποχρεωτικός. Τοποθέτηση κοντά στη γκαραζόπορτα — ορατός από οπουδήποτε. Ανανέωση κάθε 2 χρόνια.',
        tags: ['Αγορά', '~25–40€'] },
      { id: '5.3', title: 'Σύστημα αερισμού ζώνης βαφής',
        desc: 'Απλός εξαεριστήρας (axial fan) κοντά στην Πόρτα 2. Χρήση μόνο όταν ανοίγει η πόρτα. Αρκεί για ερασιτεχνική βαφή.',
        tags: ['~30–60€'] },
      { id: '5.4', title: 'Φωτισμός εργασίας πάγκου (επιτραπέζιος)',
        desc: 'Ένας LED φωτισμός πάγκου (clamp lamp ή magnetic) για λεπτές εργασίες. Συμπλήρωμα στο κεντρικό LED — εξαλείφει σκιές κατά την επεξεργασία.',
        tags: ['~20–40€'] },
    ]
  },
];

const children = [
  new Paragraph({
    spacing: { after: 60 },
    children: [new TextRun({ text: 'ΠΛΑΝΟ ΥΛΟΠΟΙΗΣΗΣ', bold: true, size: 48, font: 'Arial', color: COLORS.black })]
  }),
  new Paragraph({
    spacing: { after: 40 },
    children: [new TextRun({ text: 'Γκαράζ Εργαστήριο — Σαντορίνη', bold: false, size: 28, font: 'Arial', color: COLORS.darkgray })]
  }),
  new Paragraph({
    spacing: { after: 40 },
    children: [new TextRun({ text: 'Ιάκωβος Δακουτρός  ·  10μ × 4μ  ·  40 τ.μ.  ·  Ύψος 5μ', size: 20, font: 'Arial', color: COLORS.darkgray, italics: true })]
  }),
  divider(COLORS.lightgray),
  new Paragraph({ spacing: { after: 200 }, children: [] }),

  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [3120, 3120, 3120],
    rows: [new TableRow({ children: [
      new TableCell({ borders, width: { size: 3120, type: WidthType.DXA },
        shading: { fill: COLORS.gray, type: ShadingType.CLEAR },
        margins: { top: 140, bottom: 140, left: 200, right: 200 },
        verticalAlign: VerticalAlign.CENTER,
        children: [
          new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 20 }, children: [new TextRun({ text: '5', bold: true, size: 40, font: 'Arial', color: COLORS.black })] }),
          new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 0 }, children: [new TextRun({ text: 'Φάσεις εργασίας', size: 18, font: 'Arial', color: COLORS.darkgray })] })
        ]
      }),
      new TableCell({ borders, width: { size: 3120, type: WidthType.DXA },
        shading: { fill: COLORS.gray, type: ShadingType.CLEAR },
        margins: { top: 140, bottom: 140, left: 200, right: 200 },
        verticalAlign: VerticalAlign.CENTER,
        children: [
          new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 20 }, children: [new TextRun({ text: '~12', bold: true, size: 40, font: 'Arial', color: COLORS.black })] }),
          new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 0 }, children: [new TextRun({ text: 'Εβδομάδες συνολικά', size: 18, font: 'Arial', color: COLORS.darkgray })] })
        ]
      }),
      new TableCell({ borders, width: { size: 3120, type: WidthType.DXA },
        shading: { fill: COLORS.gray, type: ShadingType.CLEAR },
        margins: { top: 140, bottom: 140, left: 200, right: 200 },
        verticalAlign: VerticalAlign.CENTER,
        children: [
          new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 20 }, children: [new TextRun({ text: '2', bold: true, size: 40, font: 'Arial', color: COLORS.black })] }),
          new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 0 }, children: [new TextRun({ text: 'Αγορές που λείπουν', size: 18, font: 'Arial', color: COLORS.darkgray })] })
        ]
      }),
    ]})]
  }),

  new Paragraph({ spacing: { after: 300 }, children: [] }),
];

phases.forEach((phase, i) => {
  children.push(phaseHeader(phase.num, phase.title, phase.subtitle, phase.bg, phase.textColor));
  children.push(new Paragraph({ spacing: { after: 80 }, children: [] }));
  children.push(stepTable(phase.steps));
  children.push(new Paragraph({ spacing: { after: i < phases.length - 1 ? 280 : 200 }, children: [] }));
});

children.push(divider(COLORS.lightgray));
children.push(new Paragraph({ spacing: { after: 100 }, children: [] }));
children.push(new Paragraph({
  spacing: { after: 120 },
  children: [new TextRun({ text: 'Συνολικό εκτιμώμενο κόστος', bold: true, size: 26, font: 'Arial', color: COLORS.teal })]
}));
children.push(summaryTable());
children.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
children.push(new Paragraph({
  spacing: { after: 60 },
  children: [new TextRun({
    text: 'Σημείωση: Το κόστος είναι ενδεικτικό. Δεν περιλαμβάνει εργατικά ηλεκτρολόγου (~100–200€) ούτε τυχόν επισκευές τοίχων/δαπέδου που θα αποκαλυφθούν κατά το αδειάσιμο.',
    size: 17, font: 'Arial', color: COLORS.darkgray, italics: true
  })]
}));

const doc = new Document({
  numbering: {
    config: [
      {
        reference: 'bullets',
        levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }]
      }
    ]
  },
  styles: {
    default: { document: { run: { font: 'Arial', size: 20 } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 36, bold: true, font: 'Arial', color: COLORS.black },
        paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 26, bold: true, font: 'Arial', color: COLORS.darkgray },
        paragraph: { spacing: { before: 280, after: 80 }, outlineLevel: 1 } },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 }
      }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: COLORS.lightgray, space: 1 } },
          spacing: { after: 120 },
          children: [new TextRun({ text: 'Πλάνο Υλοποίησης Γκαράζ · Σαντορίνη · Ιάκωβος Δακουτρός', size: 16, font: 'Arial', color: COLORS.darkgray })]
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          border: { top: { style: BorderStyle.SINGLE, size: 4, color: COLORS.lightgray, space: 1 } },
          spacing: { before: 80 },
          children: [
            new TextRun({ text: 'Σελίδα ', size: 16, font: 'Arial', color: COLORS.darkgray }),
            new TextRun({ children: [PageNumber.CURRENT], size: 16, font: 'Arial', color: COLORS.darkgray }),
            new TextRun({ text: ' από ', size: 16, font: 'Arial', color: COLORS.darkgray }),
            new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 16, font: 'Arial', color: COLORS.darkgray }),
          ]
        })]
      })
    },
    children
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync('/mnt/user-data/outputs/garage-plan.docx', buffer);
  console.log('OK');
});

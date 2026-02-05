// Mock API data that will be replaced by FastAPI calls
export const mockDashboardStats = {
  valides: 124,
  enCours: 32,
  refuses: 8
}

export const mockActivityData = [12, 20, 8, 16, 24, 18, 22]

export const mockValidationRateData = [40, 50, 55, 60, 58, 64, 70]

export const mockFluxData = {
  valides: [
    {
      id: 'F-101',
      nom: 'Flux A',
      description: 'Import quotidien des ventes',
      comment: 'Bon jeu de données',
      fileSize: '3.2 MB',
      csvContent: 'id,region,montant\n1,North,100\n2,South,200',
      stats: { exploitablePct: 92, rows: 120000, lastRun: '2026-02-04' },
      sampleQueries: [
        { name: 'Total ventes (depuis 2026-02-01)', query: "SELECT COUNT(*) FROM ventes WHERE date >= '2026-02-01'" },
        { name: 'Montant par région', query: "SELECT region, SUM(montant) FROM ventes GROUP BY region" }
      ],
      tableData: [ { cle: 'A1', valeur: 123 }, { cle: 'A2', valeur: 456 } ]
    },
    {
      id: 'F-102',
      nom: 'Flux B',
      description: 'Synchronisation fournisseurs',
      comment: '',
      fileSize: '1.4 MB',
      csvContent: 'id,nom,actif\n10,Alpha,1\n11,Beta,1',
      stats: { exploitablePct: 88, rows: 54000, lastRun: '2026-02-03' },
      sampleQueries: [{ name: 'Fournisseurs actifs', query: "SELECT * FROM fournisseurs WHERE actif = 1" }],
      tableData: [ { cle: 'B1', valeur: 'X' } ]
    }
  ],
  encours: [
    {
      id: 'F-201',
      nom: 'Flux C',
      description: 'Chargement logs serveur',
      fileSize: '600 KB',
      csvContent: 'time,level,message\n2026-02-05T10:00:00Z,INFO,started',
      stats: { exploitablePct: 60, rows: 20000, lastRun: '2026-02-05' },
      sampleQueries: [{ name: 'Nombre d\'erreurs (logs)', query: "SELECT COUNT(*) FROM logs WHERE level = 'ERROR'" }],
      tableData: [ { cle: 'C1', valeur: 10 } ]
    },
    {
      id: 'F-202',
      nom: 'Flux D',
      description: 'Import prospects marketing',
      fileSize: '240 KB',
      csvContent: 'id,email,source\n201,a@ex.com,campaign',
      stats: { exploitablePct: 72, rows: 8000, lastRun: '2026-02-05' },
      sampleQueries: [{ name: 'Prospects (campagne)', query: "SELECT * FROM prospects WHERE source = 'campaign'" }],
      tableData: [ { cle: 'D1', valeur: 7 } ]
    }
  ],
  refuses: [
    {
      id: 'F-301',
      nom: 'Flux X',
      description: 'Flux expérimental',
      comment: 'Colonnes manquantes',
      errors: [ 'Missing column: id_client', 'Invalid date format in column date' ],
      fileSize: '6 KB',
      csvContent: 'bad,row',
      stats: { exploitablePct: 10, rows: 120, lastRun: '2026-01-30' },
      sampleQueries: [{ name: 'Aperçu expérimental', query: "SELECT * FROM experimental LIMIT 10" }],
      tableData: [ { cle: 'X1', valeur: 'err' } ]
    }
  ]
}

export const mockNettoyageData = [
  { id: 'N-1', type: 'Incohérence date' },
  { id: 'N-2', type: 'Doublon' },
  { id: 'N-3', type: 'Manque info' }
]

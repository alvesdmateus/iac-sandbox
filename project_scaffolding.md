iac-sandbox/
├── .github/
│   └── workflows/
│       ├── preview.yml          # PR: pulumi preview
│       ├── deploy.yml            # Merge: pulumi up
│       └── cleanup.yml           # Scheduled: teardown expired stacks
├── infra/
│   ├── __main__.py              # Pulumi entrypoint
│   ├── Pulumi.yaml              # Project config
│   ├── requirements.txt
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py              # Abstract provider interface
│   │   ├── gcp.py               # GCP-specific implementation
│   │   └── aws.py               # (Future) AWS implementation
│   ├── cluster/
│   │   ├── __init__.py
│   │   └── kubernetes.py        # K8s cluster provisioning
│   └── application/
│       ├── __init__.py
│       └── sudoku_app.py        # K8s manifests for sudoku game
├── config/
│   ├── dev.yaml                 # Per-environment configuration
│   └── prod.yaml
├── scripts/
│   └── generate_stack_name.py  # User-based stack naming
└── README.md
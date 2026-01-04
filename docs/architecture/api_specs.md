# API Specifications

## Endpoints

### POST `/analyze_cdc`
- **Input**: `{"cdc_text": "..."}`
- **Output**: `CadrageReport`

### POST `/generate_c4`
- **Input**: `{"requirements": {...}}`
- **Output**: `{"diagram": "mermaid code"}`

### POST `/generate_code`
- **Input**: `{"adr": {...}, "c4_diagram": {...}}`
- **Output**: `SOLIDCode`

# Vulnerable App Templates for Dynamic Target Generation

This directory contains vulnerable application templates that are used to generate real, dynamic targets for AI testing scenarios.

## Structure

Each template follows this structure:
```
template_name/
├── app/                 # The vulnerable application code
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Optional: for multi-service apps
├── config.json         # Template metadata and configuration
└── mutate.py           # Optional: AI mutation script
```

## Template Types

### Web Applications
- **sql_injection_basic/**: Simple SQL injection vulnerability
- **xss_reflected/**: Reflected XSS vulnerability
- **file_upload/**: Unsafe file upload vulnerability
- **auth_bypass/**: Authentication bypass vulnerability

### API Applications
- **api_sql_injection/**: API with SQL injection
- **api_jwt_weak/**: Weak JWT implementation
- **api_rate_limit_bypass/**: Rate limiting bypass

### Infrastructure
- **weak_ssh/**: SSH with weak configuration
- **docker_escape/**: Docker container escape scenario

## Usage

Templates are automatically selected and provisioned by the `DynamicTargetService` based on:
- Scenario difficulty level
- AI's learning history and strengths/weaknesses
- Previous successful/failed attacks
- Randomization for variety

## Configuration

Each `config.json` contains:
```json
{
  "name": "Template Name",
  "difficulty": "easy|medium|hard|expert",
  "vulnerabilities": ["sql_injection", "xss"],
  "ports": [8080],
  "credentials": {
    "admin": "admin:password",
    "user": "user:password"
  },
  "mutation_options": {
    "code_complexity": "low|medium|high",
    "vuln_obfuscation": true,
    "randomization": true
  }
}
``` 
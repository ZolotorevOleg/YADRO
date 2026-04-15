# FINDINGS

## Trivy scan summary

The image `currency-service:latest` was scanned with Trivy.

Scan command:
```
trivy image --severity CRITICAL,HIGH --ignore-unfixed --format json --output trivy-report.json currency-service
```

## Results

No `CRITICAL` or `HIGH` vulnerabilities were found in the image according to the selected scan parameters.

## Notes

- The scan was limited to `CRITICAL` and `HIGH` severity levels.
- Unfixed vulnerabilities were ignored using `--ignore-unfixed`.
- Therefore, lower-severity findings or ignored unfixed issues are not included in this report.

## Hardening changes

The hardened Docker Compose configuration includes:

- running the container with a read-only filesystem
- temporary writable storage only through `/tmp`
- `no-new-privileges:true`
- `cap_drop: ALL`
- process and resource limits
- isolated bridge network

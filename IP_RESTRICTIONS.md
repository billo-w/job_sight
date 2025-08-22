# IP Restrictions for Testing Environments

This document explains how IP restrictions work in the Job Sight application for security.

## Overview

The application now supports IP restrictions for testing environments while keeping production open to the public. This ensures that:

- **Production (main branch)**: Open to everyone (public job search app)
- **Testing environments (feature branches)**: Restricted to specific IP addresses for security

## How It Works

### 1. Environment Variables

The application uses these environment variables to control IP restrictions:

- `ENABLE_IP_RESTRICTIONS`: Set to "true" to enable restrictions, "false" to disable
- `ALLOWED_IPS`: Comma-separated list of allowed IP addresses (supports CIDR notation)

### 2. IP Restriction Logic

The application checks every request against the allowed IP list:

```python
def check_ip_restriction():
    # Check if restrictions are enabled
    if not os.environ.get('ENABLE_IP_RESTRICTIONS', 'false').lower() == 'true':
        return True  # No restrictions
    
    # Get allowed IPs
    allowed_ips = os.environ.get('ALLOWED_IPS', '').split(',')
    
    # Check if client IP is allowed
    client_ip = request.remote_addr
    # ... IP checking logic
```

### 3. Supported IP Formats

- **Single IP**: `192.168.1.100`
- **CIDR Range**: `192.168.1.0/24` (allows 192.168.1.0 to 192.168.1.255)
- **Allow All**: `0.0.0.0/0`

## CI/CD Configuration

### Production Deployment (main branch)

```yaml
# No IP restrictions for production
TF_VAR_enable_ip_restrictions: "false"
TF_VAR_allowed_ips: '["0.0.0.0/0"]'
```

### Testing Deployment (feature branches)

```yaml
# IP restrictions enabled for testing
TF_VAR_enable_ip_restrictions: "true"
TF_VAR_allowed_ips: '["YOUR_IP_ADDRESS"]'
```

## Setup Instructions

### 1. Add GitHub Secret

Add your IP address to GitHub repository secrets:

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Add a new secret called `TESTING_ALLOWED_IPS`
4. Set the value to your IP address(es), e.g.:
   - Single IP: `192.168.1.100`
   - Multiple IPs: `192.168.1.100,10.0.0.50`
   - IP Range: `192.168.1.0/24`

### 2. Find Your IP Address

To find your current IP address:

```bash
# On macOS/Linux
curl ifconfig.me

# Or visit
# https://whatismyipaddress.com/
```

### 3. Testing the Setup

1. Create a feature branch: `git checkout -b feature/test-ip-restrictions`
2. Push the branch: `git push origin feature/test-ip-restrictions`
3. The CI/CD will deploy a testing environment with IP restrictions
4. Try accessing the testing URL from:
   - **Your IP**: Should work ✅
   - **Different IP**: Should be blocked ❌

## Example IP Configurations

### Office Network
```
TESTING_ALLOWED_IPS: 192.168.1.0/24,10.0.0.0/8
```

### Home Office
```
TESTING_ALLOWED_IPS: 203.0.113.45
```

### Multiple Locations
```
TESTING_ALLOWED_IPS: 192.168.1.100,203.0.113.45,198.51.100.0/24
```

## Security Benefits

1. **Testing Isolation**: Only authorized users can access testing environments
2. **Data Protection**: Prevents unauthorized access to test data
3. **Cost Control**: Reduces risk of abuse on testing environments
4. **Compliance**: Helps meet security requirements for sensitive testing

## Troubleshooting

### Access Denied Error

If you get "Access denied" when trying to access a testing environment:

1. Check your current IP: `curl ifconfig.me`
2. Verify your IP is in the `TESTING_ALLOWED_IPS` secret
3. Update the secret if needed
4. Redeploy the testing environment

### Dynamic IP Addresses

If your IP address changes frequently:

1. Use a broader range: `203.0.113.0/24`
2. Consider using a VPN with a static IP
3. Update the secret when your IP changes

### Testing from Multiple Locations

Add all your IP addresses to the secret:

```
TESTING_ALLOWED_IPS: 192.168.1.100,203.0.113.45,198.51.100.50
```

## Notes

- IP restrictions are applied at the application level
- The restriction check happens before any request processing
- Failed requests return HTTP 403 (Forbidden)
- Production environments always allow all IPs for public access

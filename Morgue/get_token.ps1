# Check if the user is already logged in
$account = az account show 2>&1

if ($account -like "*Please run 'az login'*") {
    Write-Output "User not logged in. Initiating az login..."
    az login
} else {
    Write-Output "User already logged in."
}

# Run the Azure CLI command to get the access token
$tokenResponse = az account get-access-token --resource-type ms-graph | ConvertFrom-Json

# Extract the access token
$accessToken = $tokenResponse.accessToken

# Output only the access token
$accessToken

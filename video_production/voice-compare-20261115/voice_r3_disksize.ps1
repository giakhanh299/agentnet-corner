$ErrorActionPreference = "Continue"
Get-ChildItem C:\Users\w\agentnet-corner\ai-stack -Directory | ForEach-Object {
    $s = (Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
    "{0} : {1:N1} GB" -f $_.Name, ($s / 1GB)
}
$drv = Get-PSDrive C
"C: free {0:N1} GB" -f ($drv.Free / 1GB)

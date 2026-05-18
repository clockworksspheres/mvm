# Hyper-V issues

May need to put together an ansible script for getting these things set up for each VM...  Or having a setup method in the vmctl command (concrete OS /hypervisor methods for getting a VM setup)

## Windows VM comes up with a blue screen, missing the login, and it only shows the power button and one other button in the bottom right

### It is running in Enhanced mode, and Remote Desktop has control of the VM

Run the following and it will be fixed for all VM's:

``` bash
Set-VMHost -EnableEnhancedSessionMode $false   
```

## Hyper-V vm is running in headless mode - how do I change that so mvm runs in gui mode?

``` bash
Start-VM -Name "YourVMName" -Passthru | % { vmconnect.exe $_.ComputerName $_.VMName }   
```

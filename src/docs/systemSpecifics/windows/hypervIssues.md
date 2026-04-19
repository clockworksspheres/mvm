# Hyper-V issues

## Windows VM comes up with a blue screen, missing the login, and it only shows the power button and one other button in the bottom right

### It is running in Enhanced mode, and Remote Desktop has control of the VM

Run the following and it will be fixed for all VM's:

```
Set-VMHost -EnableEnhancedSessionMode $false   
```
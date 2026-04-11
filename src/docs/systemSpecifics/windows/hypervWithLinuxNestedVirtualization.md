

# hyperv setup for nested virtualization, linux guest using kvm, oracle virtualbox

You’re trying to stack **Hyper-V → Linux (KVM) → VirtualBox**, which is doable—but only if you get nested virtualization and CPU passthrough exactly right. Here’s the reality and a working setup path.

---

## ⚠️ First: What actually works

- ✅ Hyper-V supports **nested virtualization**
    
- ✅ Linux KVM can run inside a Hyper-V VM
    
- ⚠️ VirtualBox _inside_ that KVM VM is **possible but fragile and slow**
    
- ❌ You won’t get near-native performance at the 3rd layer
    

If your goal is experimentation/testing → fine  
If your goal is performance → stop at KVM or Hyper-V

---

## 🧱 Architecture

```
Host (Windows with Hyper-V)
  └── Linux VM (KVM enabled)
        └── VirtualBox VM
```

---

## 1️⃣ Enable nested virtualization in Hyper-V

Run PowerShell **as Administrator**:

```powershell
Set-VMProcessor -VMName "YourLinuxVM" -ExposeVirtualizationExtensions $true
```

Also recommended:

```powershell
Set-VMProcessor -VMName "YourLinuxVM" -Count 4
Set-VMMemory -VMName "YourLinuxVM" -DynamicMemoryEnabled $false
```

👉 Then **fully shut down** the VM (not restart):

```powershell
Stop-VM "YourLinuxVM"
```

---

## 2️⃣ Configure Linux guest for KVM

Inside your Linux VM:

### Check virtualization support

```bash
egrep -c '(vmx|svm)' /proc/cpuinfo
```

If > 0 → good

---

### Install KVM stack

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install -y qemu-kvm libvirt-daemon-system libvirt-clients virt-manager
```

---

### Enable KVM modules

```bash
lsmod | grep kvm
```

If missing:

```bash
sudo modprobe kvm
sudo modprobe kvm_intel   # or kvm_amd
```

---

### Verify KVM works

```bash
sudo kvm-ok
```

Expected:

```
KVM acceleration can be used
```

---

## 3️⃣ Performance tweak (important)

Hyper-V nested virtualization works best with:

### Disable secure boot in VM

Hyper-V Manager → VM → Settings → Security

---

### Use CPU passthrough mode (libvirt)

Edit VM config:

```bash
virsh edit your-vm
```

Set:

```xml
<cpu mode='host-passthrough'/>
```

---

## 4️⃣ Install VirtualBox inside Linux

```bash
sudo apt install -y virtualbox
```

---

### ⚠️ Critical limitation

VirtualBox normally wants **VT-x/AMD-V**, which is already virtualized.

So:

- It will run in **software / limited mode**
    
- Or fail unless you force fallback
    

---

### Force VirtualBox to run without VT-x

```bash
VBoxManage modifyvm "VM_NAME" --hwvirtex off
```

---

## 5️⃣ Alternative (better approach)

Instead of stacking 3 hypervisors:

### Option A (recommended)

```
Hyper-V → Linux → KVM (stop here)
```

Use KVM only

---

### Option B

```
Hyper-V → Linux → Docker / containers
```

Much faster and simpler

---

### Option C (if you need VirtualBox specifically)

Run VirtualBox **directly on host**, not inside KVM

---

## 🚨 Common problems

### ❌ “KVM not available”

Fix:

- Forgot `ExposeVirtualizationExtensions`
    
- VM not powered off after change
    

---

### ❌ VirtualBox crashes

Fix:

- Disable VT-x in VBox (`--hwvirtex off`)
    
- Accept degraded performance
    

---

### ❌ Extremely slow performance

That’s expected:

- You’re doing **triple virtualization**
    

---

## 💡 Practical advice

If your goal is:

- **Testing nested virtualization** → this setup is fine
    
- **Running real workloads** → don’t use VirtualBox inside KVM inside Hyper-V
    

---

## 👍 If you want

I can give you:

- A **fully automated PowerShell + Bash setup script**
    
- A **CI-friendly nested virtualization config (Jenkins + KVM)**
    
- Or a **much cleaner architecture for your use case**
    

Just tell me your end goal (lab, CI, dev env, etc.) and I’ll optimize it.


# hyperv -> linux -> virtualbox

Short version: **Hyper-V → Linux → VirtualBox** works, but **VirtualBox will NOT get real hardware virtualization (VT-x/AMD-V)** in that setup. It will run in a degraded/software mode, and performance will be poor.

If you still want it (lab/testing), here’s the clean way to do it.

---

## 🧱 Architecture

```
Windows (Hyper-V)
  └── Linux VM
        └── VirtualBox VMs (no VT-x)
```

---

## 1️⃣ Enable nested virtualization (required even if VBox won’t fully use it)

On Windows host (PowerShell as Admin):

```powershell
Set-VMProcessor -VMName "LinuxVM" -ExposeVirtualizationExtensions $true
Stop-VM "LinuxVM"
Start-VM "LinuxVM"
```

---

## 2️⃣ Create a proper Linux VM (important settings)

In Hyper-V:

- **Generation 2 VM**
    
- **Disable Secure Boot** (or set to Microsoft UEFI CA for Ubuntu)
    
- CPU: **at least 2–4 cores**
    
- RAM: **8GB+ recommended**
    
- Disk: SSD-backed if possible
    

---

## 3️⃣ Install VirtualBox inside Linux

Ubuntu/Debian example:

```bash
sudo apt update
sudo apt install -y virtualbox
```

Verify:

```bash
vboxmanage --version
```

---

## 4️⃣ Critical: Disable hardware virtualization in VirtualBox

Because Hyper-V does not pass VT-x cleanly to VirtualBox, you must force software mode.

For each VM:

```bash
VBoxManage modifyvm "YourVM" --hwvirtex off
VBoxManage modifyvm "YourVM" --nestedpaging off
```

Optional (helps stability):

```bash
VBoxManage modifyvm "YourVM" --paravirtprovider none
```

---

## 5️⃣ Create VirtualBox VM with safe settings

Inside VirtualBox:

- OS: Linux (lighter distros recommended)
    
- CPU: **1 core**
    
- RAM: **1–2GB**
    
- Graphics: **VMSVGA**
    
- Disable 3D acceleration
    

👉 Heavy OSes (Windows guests) will be painfully slow.

---

## ⚠️ What to expect

### Performance

- Boot times: slow
    
- CPU: heavily throttled
    
- I/O: noticeable lag
    

### Limitations

- No nested VT-x → no 64-bit acceleration benefits
    
- Some OS installers may fail or hang
    
- GUI lag in desktop environments
    

---

## 🚨 Common failures

### “VT-x is not available”

Expected — you disabled it. Ignore.

---

### VM won’t start / Guru Meditation

Fix:

```bash
VBoxManage modifyvm "YourVM" --hwvirtex off
```

---

### Extremely slow UI

Use:

- XFCE / LXDE instead of GNOME/KDE
    
- Headless mode:
    

```bash
VBoxHeadless --startvm "YourVM"
```

---

## 💡 Better alternatives (strongly recommended)

If your goal is…

### ✔ Run multiple VMs

👉 Use **KVM inside Linux** instead of VirtualBox  
(it _does_ work with nested virtualization)

---

### ✔ Cross-platform dev/testing

👉 Use:

- Docker / Podman
    
- or KVM + cloud images
    

---

### ✔ Need VirtualBox specifically

👉 Run it:

- Directly on Windows **without Hyper-V**, OR
    
- Inside a **non-Hyper-V hypervisor** (like VMware Workstation)
    

---

## 🧠 Bottom line

- ✔ Works: Hyper-V → Linux → VirtualBox
    
- ❌ Not hardware accelerated
    
- ⚠️ Only useful for light testing / experimentation
    

---

If you tell me _why_ you need VirtualBox in that stack (CI? cross-platform testing? legacy VM?), I can give you a much cleaner setup that performs 10–50× better.


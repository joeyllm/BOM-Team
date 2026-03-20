# 🔐 WireGuard VPN Setup

To access the BOM Nowcasting compute infrastructure (including our JupyterHub and the L4 GPUs), you must first connect to our secure internal network using **WireGuard**.

Our server sits behind a firewall and is not exposed to the public internet. WireGuard creates a secure, encrypted tunnel from your laptop directly to our environment.

---

## 🛠️ Step 1: Install the WireGuard Client

You will need to install the WireGuard application for your specific operating system.

* **Windows:** Download the installer from the [official WireGuard website](https://www.wireguard.com/install/).
* **macOS:** Download the WireGuard app directly from the [Mac App Store](https://apps.apple.com/us/app/wireguard/id1451685025).
* **Linux (Ubuntu/Debian):** Run the following command in your terminal:
  `sudo apt install wireguard`

---

## 🔑 Step 2: Generate and Provide Your Public Key

Unlike some VPNs where you just log in with a password, WireGuard uses cryptographic keys. You need to generate a key pair on your machine and give your **Public Key** to **Matthew Altenburg**.

**How to get your Public Key:**
1. Open the WireGuard application.
2. Click **"Add Tunnel"** (or the **"+"** icon) and select **"Add empty tunnel"** (or press Ctrl+N / Cmd+N).
3. A window will pop up showing an automatically generated **Private Key** and **Public Key**.
4. Copy the **Public Key** string and send it to Matthew. 
*(Note: Never share your Private Key with anyone!)*

---

## 📥 Step 3: Receive Your Configuration

Once you provide your Public Key, Matthew will configure your access on the server side. 

On the **first day of the project**, you will be given:
* Your unique **Tunnel IP address**
* The server endpoint and peer configuration details.

You will simply paste these details into the empty tunnel window you opened in Step 2, name the tunnel (e.g., `BOM-Nowcasting`), and click **Save**.

---

## 🟢 Step 4: Connect to the Network

Once your profile is saved:
1. Select the BOM Nowcasting tunnel from your list in the WireGuard app.
2. Click the **"Activate"** or **"Connect"** button.
3. The status should change to **Active**, and you should see data starting to transfer (Tx/Rx).

---

## ✅ Step 5: Verify Your Connection

To confirm that your VPN tunnel is working correctly and you have access to the compute environment:

1. Open your web browser.
2. Navigate to the JupyterHub login page at: `http://10.55.0.245`
3. If the page loads and prompts you to sign in with GitHub, your connection is successful! 🎉

---

## ⚠️ Troubleshooting & Rules

* **Disconnect when finished:** Please deactivate the VPN when you are not actively working on the project.
* **Can't reach the server?** Double-check that WireGuard says "Active." If it is active but the `10.55.0.245` page is timing out, try deactivating and reactivating the tunnel. 
* **Still having issues?** If you cannot connect after following these steps, reach out to Matthew for support.

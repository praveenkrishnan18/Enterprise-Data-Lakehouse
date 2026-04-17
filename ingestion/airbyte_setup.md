# Airbyte Setup Guide

Airbyte is used to extract data from **HubSpot** (contacts via API) and **Mailchimp**
(campaigns via Google Sheets) and load them into a **PostgreSQL** staging database —
all running locally inside Docker via the `abctl` CLI.

---

## Prerequisites

- Docker Desktop installed and running (WSL2 backend on Windows)
- `abctl.exe` binary in `ingestion/airbyte/bin/`
  (download from https://github.com/airbytehq/abctl/releases)

---

## 1. Deploy Airbyte Locally

```powershell
cd ingestion\airbyte\bin

# Initialise configuration
.\abctl init

# Deploy Airbyte containers
.\abctl deploy

# Verify status
.\abctl local status
```

Airbyte UI: **http://localhost:8000**

---

## 2. Retrieve Login Credentials

```powershell
.\abctl local credentials
```

Example output:
```
Email:    admin@example.com
Password: JwsFIfvTLELzrqArQYMbHg2SDF15oup7
```

---

## 3. Configure Sources

### Source 1 — HubSpot (Contacts)

| Field | Value |
|---|---|
| Connector | HubSpot |
| Authentication | Private App API Token |
| Streams | Contacts |

### Source 2 — Mailchimp (via Google Sheets)

| Field | Value |
|---|---|
| Connector | Google Sheets |
| Sheet URL | Your exported Mailchimp campaign sheet URL |

---

## 4. Configure Destination — PostgreSQL

| Parameter | Value |
|---|---|
| Host | `host.docker.internal` |
| Port | `5432` |
| Database | `airbyte` |
| Schema | `public` |
| Username | `airbyte` |
| Password | `password` |

---

## 5. Local File System Access (optional)

To allow Airbyte to access local files, edit the `.env` inside the Airbyte folder:

```env
LOCAL_ROOT=C://Project//Storage
LOCAL_DOCKER_MOUNT=/local
HACK_LOCAL_ROOT_PARENT=C://Project
```

---

## 6. Run a Sync

1. Open http://localhost:8000 and log in
2. Go to **Connections** → select your HubSpot or Mailchimp connection
3. Click **Sync Now**
4. Once complete, open pgAdmin to verify data landed in PostgreSQL

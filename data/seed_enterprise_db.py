"""Enterprise Data Warehouse Seeder (DuckDB).
Generates realistic B2B SaaS accounts, leads lifecycle, marketing campaigns, and subscription tables.
"""

import duckdb
from pathlib import Path
from datetime import datetime, timedelta
import random

from src.config import Config

def seed_database(db_path: Path = Config.DB_PATH) -> None:
    """Creates tables and populates realistic B2B SaaS enterprise data."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = duckdb.connect(str(db_path))
    
    print(f"[DB] Initializing enterprise warehouse at {db_path}...")
    
    # 1. Accounts Table
    conn.execute("""
    CREATE OR REPLACE TABLE accounts (
        account_id VARCHAR PRIMARY KEY,
        account_name VARCHAR NOT NULL,
        tier VARCHAR NOT NULL, -- Enterprise, Mid-Market, SMB
        industry VARCHAR NOT NULL,
        annual_contract_value_usd DECIMAL(12, 2) NOT NULL,
        status VARCHAR NOT NULL, -- Active, Churned, In-Pilot
        health_score INTEGER NOT NULL, -- 0-100
        region VARCHAR NOT NULL, -- North America, EMEA, APAC, LATAM
        created_at TIMESTAMP NOT NULL
    );
    """)

    # 2. Leads Table (Lead Lifecycle & Attribution)
    conn.execute("""
    CREATE OR REPLACE TABLE leads (
        lead_id VARCHAR PRIMARY KEY,
        account_id VARCHAR,
        contact_name VARCHAR NOT NULL,
        contact_email VARCHAR NOT NULL,
        lead_source VARCHAR NOT NULL, -- Webinar, Organic Search, D&B Inbound, Partner
        lead_score INTEGER NOT NULL, -- 0-100
        lifecycle_stage VARCHAR NOT NULL, -- New, MQL, SQL, Opportunity, Won
        lead_leakage_flag BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP NOT NULL,
        converted_at TIMESTAMP
    );
    """)

    # 3. Campaigns Table (Marketing Technology ROI)
    conn.execute("""
    CREATE OR REPLACE TABLE campaigns (
        campaign_id VARCHAR PRIMARY KEY,
        campaign_name VARCHAR NOT NULL,
        channel VARCHAR NOT NULL, -- Paid Search, ABM Display, Email Nurture, Event
        allocated_budget_usd DECIMAL(10, 2) NOT NULL,
        actual_spend_usd DECIMAL(10, 2) NOT NULL,
        target_mql_count INTEGER NOT NULL,
        actual_mql_count INTEGER NOT NULL,
        status VARCHAR NOT NULL -- Active, Completed, Paused
    );
    """)

    # 4. Subscriptions Table (MRR & Financial Retention)
    conn.execute("""
    CREATE OR REPLACE TABLE subscriptions (
        subscription_id VARCHAR PRIMARY KEY,
        account_id VARCHAR NOT NULL,
        plan_name VARCHAR NOT NULL, -- Enterprise Elite, Scale Pro, Growth Starter
        mrr_usd DECIMAL(10, 2) NOT NULL,
        start_date DATE NOT NULL,
        renewal_date DATE NOT NULL,
        auto_renew BOOLEAN NOT NULL,
        FOREIGN KEY (account_id) REFERENCES accounts (account_id)
    );
    """)

    # 5. Query Audit Telemetry Table
    conn.execute("""
    CREATE OR REPLACE TABLE query_telemetry (
        telemetry_id VARCHAR PRIMARY KEY,
        natural_query VARCHAR NOT NULL,
        generated_sql VARCHAR NOT NULL,
        execution_time_ms DOUBLE NOT NULL,
        row_count INTEGER NOT NULL,
        status VARCHAR NOT NULL, -- SUCCESS, BLOCKED, ERROR
        reflection_iterations INTEGER DEFAULT 0,
        executed_at TIMESTAMP NOT NULL
    );
    """)

    # Populate Data
    random.seed(42)
    
    # Insert Accounts (100 accounts)
    industries = ["Healthcare & Life Sciences", "Fintech & Banking", "Manufacturing", "Retail & E-commerce", "SaaS & Cloud"]
    tiers = ["Enterprise", "Mid-Market", "SMB"]
    regions = ["North America", "EMEA", "APAC", "LATAM"]
    statuses = ["Active", "Active", "Active", "In-Pilot", "Churned"]
    
    accounts_data = []
    base_date = datetime(2024, 1, 1)
    
    company_prefixes = ["Apex", "Omni", "Global", "Cyber", "Vanguard", "Starlight", "Cortex", "Novis", "Pulse", "Stratum"]
    company_suffixes = ["Health", "Dynamics", "Systems", "Technologies", "Logistics", "Financial", "Data", "Labs", "Cloud", "Robotics"]
    
    for i in range(1, 101):
        acc_id = f"ACC-{i:04d}"
        name = f"{random.choice(company_prefixes)} {random.choice(company_suffixes)} {i}"
        tier = random.choices(tiers, weights=[0.25, 0.45, 0.30])[0]
        ind = random.choice(industries)
        
        if tier == "Enterprise":
            acv = round(random.uniform(120000.0, 750000.0), 2)
        elif tier == "Mid-Market":
            acv = round(random.uniform(35000.0, 119000.0), 2)
        else:
            acv = round(random.uniform(8000.0, 34000.0), 2)
            
        status = random.choice(statuses)
        health = random.randint(35, 99) if status != "Churned" else random.randint(10, 45)
        reg = random.choice(regions)
        created = base_date + timedelta(days=random.randint(0, 300))
        
        accounts_data.append((acc_id, name, tier, ind, acv, status, health, reg, created))
        
    conn.executemany("""
    INSERT INTO accounts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, accounts_data)
    
    # Insert Campaigns (10 campaigns)
    channels = ["ABM Display", "Paid Search", "Email Nurture", "Executive Roundtable", "Content Syndication"]
    campaigns_data = [
        ("CMP-001", "Q1 Enterprise AI Cloud Summit", "Executive Roundtable", 150000.0, 142500.0, 120, 145, "Completed"),
        ("CMP-002", "D&B High-Intent Healthcare ABM", "ABM Display", 85000.0, 84100.0, 90, 88, "Active"),
        ("CMP-003", "Fintech Tax Compliance Webinar", "Email Nurture", 35000.0, 31200.0, 200, 215, "Completed"),
        ("CMP-004", "Google Search: MarTech Automation", "Paid Search", 110000.0, 108900.0, 250, 195, "Active"),
        ("CMP-005", "EMEA Retail Omnichannel Push", "Content Syndication", 65000.0, 64200.0, 140, 130, "Active"),
        ("CMP-006", "Global Enterprise Security Summit", "Executive Roundtable", 175000.0, 171000.0, 150, 162, "Completed"),
        ("CMP-007", "Q2 Pipeline Acceleration Drip", "Email Nurture", 45000.0, 42000.0, 300, 310, "Active"),
        ("CMP-008", "C-Suite Tax Automation Outbound", "ABM Display", 95000.0, 93500.0, 100, 112, "Active"),
        ("CMP-009", "Manufacturing Supply Chain Summit", "Content Syndication", 55000.0, 49000.0, 80, 75, "Paused"),
        ("CMP-010", "APAC Inbound Lead Surge", "Paid Search", 70000.0, 68500.0, 180, 190, "Active"),
    ]
    conn.executemany("INSERT INTO campaigns VALUES (?, ?, ?, ?, ?, ?, ?, ?);", campaigns_data)

    # Insert Leads (300 leads)
    lead_sources = ["D&B Inbound", "Webinar", "Organic Search", "Partner", "Paid Search"]
    lifecycle_stages = ["New", "MQL", "SQL", "Opportunity", "Won"]
    leads_data = []
    
    first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Sam", "Chris", "Casey", "Pat", "Riley", "Cameron"]
    last_names = ["Smith", "Patel", "Johnson", "Sharma", "Williams", "Chen", "Davis", "Miller", "Wilson", "Kumar"]
    
    for j in range(1, 301):
        lead_id = f"LD-{j:05d}"
        acc_id = f"ACC-{random.randint(1, 100):04d}" if random.random() > 0.25 else None
        c_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        email = f"{c_name.lower().replace(' ', '.')}@example.com"
        source = random.choice(lead_sources)
        score = random.randint(20, 98)
        
        # Determine stage based on score
        if score > 85:
            stage = random.choice(["SQL", "Opportunity", "Won"])
        elif score > 60:
            stage = random.choice(["MQL", "SQL"])
        else:
            stage = random.choice(["New", "MQL"])
            
        leakage = (score >= 80 and stage == "New")  # Lead leakage anomaly!
        c_date = base_date + timedelta(days=random.randint(0, 320))
        conv_date = c_date + timedelta(days=random.randint(5, 30)) if stage in ["Opportunity", "Won"] else None
        
        leads_data.append((lead_id, acc_id, c_name, email, source, score, stage, leakage, c_date, conv_date))
        
    conn.executemany("INSERT INTO leads VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", leads_data)

    # Insert Subscriptions
    plans = ["Enterprise Elite", "Scale Pro", "Growth Starter"]
    subs_data = []
    for k in range(1, 101):
        acc = accounts_data[k-1]
        acc_id = acc[0]
        status = acc[5]
        tier = acc[2]
        
        if status != "Churned":
            sub_id = f"SUB-{k:04d}"
            plan = "Enterprise Elite" if tier == "Enterprise" else ("Scale Pro" if tier == "Mid-Market" else "Growth Starter")
            mrr = round(acc[4] / 12.0, 2)
            s_date = acc[8].date()
            r_date = s_date + timedelta(days=365)
            auto_r = random.choice([True, True, False])
            subs_data.append((sub_id, acc_id, plan, mrr, s_date, r_date, auto_r))
            
    conn.executemany("INSERT INTO subscriptions VALUES (?, ?, ?, ?, ?, ?, ?);", subs_data)
    
    print(f"[DB] Successfully seeded:")
    print(f"  • {len(accounts_data)} Accounts")
    print(f"  • {len(campaigns_data)} Campaigns")
    print(f"  • {len(leads_data)} Leads (including lead leakage test cases)")
    print(f"  • {len(subs_data)} Subscriptions")
    
    conn.close()

if __name__ == "__main__":
    seed_database()

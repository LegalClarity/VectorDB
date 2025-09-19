
**Data Models and Schemas**

**General Document Schema**

`{`  
  `"document_id": "string",`  
  `"document_type": "rental|loan|tos|other",`  
  `"metadata": {`  
    `"title": "string",`  
    `"parties": ["string"],`  
    `"jurisdiction": "string",`  
    `"language": "string",`  
    `"creation_date": "datetime",`  
    `"last_modified": "datetime"`  
  `},`  
  `"structure": {`  
    `"sections": ["object"],`  
    `"clauses": ["object"],`  
    `"tables": ["object"],`  
    `"signatures": ["object"]`  
  `},`  
  `"analysis": {`  
    `"key_terms": ["string"],`  
    `"risk_factors": ["object"],`  
    `"compliance_requirements": ["object"],`  
    `"financial_implications": "object"`  
  `}`  
`}`

**Rental Agreement Specific Schema**

`{`  
  `"rental_details": {`  
    `"property_address": "string",`  
    `"property_type": "residential|commercial",`  
    `"built_area": "number",`  
    `"furnished_status": "furnished|semi_furnished|unfurnished"`  
  `},`  
  `"financial_terms": {`  
    `"monthly_rent": "number",`  
    `"security_deposit": "number",`  
    `"maintenance_charges": "number",`  
    `"utility_responsibility": "landlord|tenant|shared"`  
  `},`  
  `"lease_terms": {`  
    `"start_date": "date",`  
    `"end_date": "date",`  
    `"renewal_terms": "object",`  
    `"notice_period": "number",`  
    `"rent_escalation": "number"`  
  `},`  
  `"legal_clauses": {`  
    `"termination_conditions": ["string"],`  
    `"penalty_clauses": ["object"],`  
    `"maintenance_obligations": ["string"],`  
    `"subletting_restrictions": "boolean"`  
  `}`  
`}`

**Loan Contract Specific Schema**

`{`  
  `"loan_details": {`  
    `"principal_amount": "number",`  
    `"loan_type": "personal|home|business|vehicle",`  
    `"purpose": "string",`  
    `"currency": "INR"`  
  `},`  
  `"interest_terms": {`  
    `"interest_rate": "number",`  
    `"rate_type": "fixed|floating",`  
    `"compounding_frequency": "monthly|quarterly|annually",`  
    `"reset_period": "number"`  
  `},`  
  `"repayment_terms": {`  
    `"loan_tenure_months": "number",`  
    `"emi_amount": "number",`  
    `"repayment_frequency": "monthly|quarterly",`  
    `"prepayment_charges": "number"`  
  `},`  
  `"security_details": {`  
    `"collateral_type": "string",`  
    `"guarantor_details": "object",`  
    `"insurance_requirements": ["string"]`  
  `},`  
  `"financial_covenants": {`  
    `"debt_to_equity_ratio": "number",`  
    `"minimum_turnover": "number",`  
    `"financial_reporting_frequency": "string"`  
  `}`  
`}`

**Terms of Service Specific Schema**

`{`  
  `"service_details": {`  
    `"service_provider": "string",`  
    `"service_description": "string",`  
    `"service_category": "digital|physical|hybrid",`  
    `"target_users": ["string"]`  
  `},`  
  `"pricing_terms": {`  
    `"pricing_model": "subscription|one_time|usage_based",`  
    `"base_cost": "number",`  
    `"billing_frequency": "monthly|annually",`  
    `"cancellation_policy": "object"`  
  `},`  
  `"user_obligations": {`  
    `"acceptable_use_policy": ["string"],`  
    `"prohibited_activities": ["string"],`  
    `"content_guidelines": ["string"]`  
  `},`  
  `"liability_terms": {`  
    `"service_level_agreements": "object",`  
    `"limitation_of_liability": "number",`  
    `"indemnification_clauses": ["string"],`  
    `"dispute_resolution": "arbitration|litigation|mediation"`  
  `},`  
  `"data_privacy": {`  
    `"data_collection": ["string"],`  
    `"data_usage": ["string"],`  
    `"data_retention_period": "number",`  
    `"third_party_sharing": "boolean"`  
  `}`  
`}`



**Legal Document Analysis: Indian Context Research**

**Document Categories Analysis**

This research focuses on three primary categories of legal documents commonly encountered in India: Rental Agreements, Loan Contracts, and Terms of Service agreements. Each category has distinct characteristics, regulatory frameworks, and structural patterns that are essential for building an AI-powered analysis system.

**1\. Rental Agreements in India**

**Legal Framework**

·       **Primary Legislation:** Transfer of Property Act, 1882; Registration Act, 1908

·       **State-Specific Laws:** Rent Control Acts vary by state

·       **Recent Developments:** Model Tenancy Act (adopted by 4 states as of 2025\)

·       **Regulatory Bodies:** State Housing Boards, Sub-Registrar offices

**Common Document Structure**

**Essential Clauses**

1\.   	**Party Identification**

o   Lessor (Landlord) details with complete address and ID proof

o   Lessee (Tenant) details with permanent and correspondence addresses

o   Witness information (minimum 2 witnesses required)

2\.   	**Property Description**

o   Complete postal address with PIN code

o   Property type (residential/commercial)

o   Built-up area and carpet area specifications

o   Floor details and apartment number

o   Common area access rights

3\.   	**Financial Terms**

o   Monthly rent amount (₹ in figures and words)

o   Security deposit (typically 2-10 months' rent)

o   Advance payment details

o   Utility bill responsibility allocation

o   Annual rent escalation clause (typically 3-10%)

4\.  	**Duration and Renewal**

o   Lease start and end dates

o   11-month rule to avoid registration (common practice)

o   Renewal terms and conditions

o   Notice period for termination (30-90 days standard)

5\.   	**Legal Compliance Clauses**

o   Stamp duty payment confirmation

o   Registration requirements (if applicable)

o   Local municipal compliance

o   Society/housing board clearances

**Rental Agreement Schema (Indian Context)**

`{`  
   `"document_metadata": {`  
 	`"document_type": "rental_agreement",`  
 	`"jurisdiction": "india",`  
 	`"state": "string",`  
 	`"registration_required": "boolean",`  
 	`"stamp_duty_value": "number",`  
 	`"creation_date": "date",`  
 	`"execution_location": "string"`  
   `},`  
    
   `"parties": {`  
 	`"lessor": {`  
   	`"name": "string",`  
   	`"father_name": "string",`  
   	`"address": "object",`  
   	`"age": "number",`  
   	`"occupation": "string",`  
   	`"pan_number": "string",`  
   	`"aadhaar_number": "string",`  
   	`"contact_details": "object"`  
 	`},`  
 	`"lessee": {`  
   	`"name": "string",`  
   	`"father_name": "string",`  
   	`"permanent_address": "object",`  
   	`"correspondence_address": "object",`  
   	`"age": "number",`  
   	`"occupation": "string",`  
   	`"monthly_income": "number",`  
   	`"pan_number": "string",`  
   	`"aadhaar_number": "string",`  
   	`"contact_details": "object"`  
 	`},`  
 	`"witnesses": ["object"]`  
   `},`  
    
   `"property_details": {`  
 	`"property_address": {`  
   	`"house_number": "string",`  
   	`"street_address": "string",`  
   	`"locality": "string",`  
   	`"city": "string",`  
   	`"state": "string",`  
   	`"pincode": "string"`  
 	`},`  
 	`"property_specifications": {`  
   	`"property_type": "residential|commercial|mixed",`  
   	`"accommodation_type": "independent_house|apartment|villa|studio",`  
   	`"total_built_area": "number",`  
   	`"carpet_area": "number",`  
   	`"floor_number": "string",`  
   	`"total_floors": "number",`  
   	`"facing_direction": "string",`  
   	`"furnishing_status": "furnished|semi_furnished|unfurnished"`  
 	`},`  
 	`"amenities_included": ["string"],`  
 	`"parking_details": "object",`  
 	`"common_area_access": ["string"]`  
   `},`  
    
   `"financial_terms": {`  
 	`"rent_details": {`  
   	`"monthly_rent": "number",`  
   	`"rent_in_words": "string",`  
   	`"due_date": "number", // Day of month`  
   	`"payment_method": "string",`  
   	`"late_payment_penalty": "object"`  
 	`},`  
 	`"deposits_and_advances": {`  
   	`"security_deposit": "number",`  
   	`"advance_rent": "number",`  
   	`"other_deposits": "object",`  
   	`"refund_conditions": "object"`  
 	`},`  
 	`"escalation_terms": {`  
       `"annual_increment_percentage": "number",`  
   	`"effective_from_year": "number",`  
       `"maximum_escalation_limit": "number"`  
 	`},`  
 	`"utility_responsibilities": {`  
   	`"electricity_bill": "landlord|tenant|shared",`  
   	`"water_charges": "landlord|tenant|shared",`  
   	`"gas_connection": "landlord|tenant|shared",`  
   	`"maintenance_charges": "landlord|tenant|shared",`  
   	`"property_tax": "landlord|tenant|shared",`  
   	`"society_charges": "landlord|tenant|shared"`  
 	`}`  
   `},`  
    
   `"lease_terms": {`  
 	`"duration": {`  
   	`"start_date": "date",`  
   	`"end_date": "date",`  
   	`"total_months": "number",`  
   	`"renewable": "boolean",`  
   	`"renewal_terms": "object"`  
 	`},`  
 	`"usage_restrictions": {`  
   	`"permitted_use": "residential_only|commercial_only|mixed",`  
   	`"subletting_allowed": "boolean",`  
   	`"guest_policy": "object",`  
   	`"pet_policy": "object",`  
   	`"modification_rights": "object"`  
 	`},`  
 	`"termination_conditions": {`  
   	`"notice_period_days": "number",`  
   	`"early_termination_penalty": "object",`  
   	`"breach_consequences": "object",`  
   	`"force_majeure_clauses": "object"`  
 	`}`  
   `},`  
    
   `"legal_clauses": {`  
 	`"maintenance_obligations": {`  
   	`"major_repairs": "landlord|tenant",`  
   	`"minor_repairs": "landlord|tenant",`  
   	`"structural_maintenance": "landlord|tenant",`  
   	`"appliance_maintenance": "object"`  
 	`},`  
 	`"compliance_requirements": {`  
   	`"local_laws_adherence": "boolean",`  
       `"society_rules_compliance": "boolean",`  
   	`"municipal_permissions": "object",`  
   	`"fire_safety_compliance": "boolean"`  
 	`},`  
 	`"dispute_resolution": {`  
   	`"jurisdiction": "string",`  
   	`"arbitration_clause": "boolean",`  
   	`"mediation_preference": "boolean",`  
   	`"applicable_courts": "string"`  
 	`}`  
   `},`  
    
   `"registration_details": {`  
 	`"stamp_paper_value": "number",`  
 	`"registration_fee": "number",`  
 	`"sub_registrar_office": "string",`  
     `"document_registration_number": "string",`  
 	`"registration_date": "date"`  
   `}`  
 `}`

**2\. Loan Contracts in India**

**Legal Framework**

·       **Primary Legislation:** Indian Contract Act, 1872; Reserve Bank of India Act, 1934

·       **Regulatory Bodies:** Reserve Bank of India (RBI), National Housing Bank (NHB)

·       **Key Regulations:** RBI Master Directions on lending, SARFAESI Act, 2002

·       **Consumer Protection:** Fair Practices Code, Banking Ombudsman Scheme

**Common Document Structure**

**Essential Components**

1\.   	**Loan Specifications**

o   Principal loan amount with purpose specification

o   Interest rate structure (fixed/floating/hybrid)

o   Loan tenure and repayment schedule

o   Processing fees and charges breakdown

2\.   	**Security and Guarantees**

o   Collateral details and valuation

o   Personal and corporate guarantees

o   Insurance requirements

o   Hypothecation/mortgage documentation

3\.   	**Financial Covenants**

o   Debt service coverage ratios

o   Loan-to-value ratios

o   Minimum turnover requirements

o   Financial reporting obligations

4\.  	**Default and Recovery**

o   Events of default definition

o   Recovery procedures

o   Enforcement of securities

o   Legal recourse mechanisms

**Loan Contract Schema (Indian Context)**

`{`  
   `"loan_metadata": {`  
 	`"loan_agreement_number": "string",`  
 	`"loan_type": "personal|home|vehicle|business|education|gold",`  
 	`"lending_institution": "object",`  
 	`"sanction_letter_reference": "string",`  
 	`"agreement_date": "date",`  
 	`"execution_location": "string",`  
     `"applicable_rbi_guidelines": "string"`  
   `},`  
    
   `"borrower_details": {`  
 	`"primary_borrower": {`  
   	`"name": "string",`  
   	`"father_name": "string",`  
   	`"date_of_birth": "date",`  
   	`"pan_number": "string",`  
   	`"aadhaar_number": "string",`  
   	`"address": "object",`  
   	`"occupation": "string",`  
   	`"annual_income": "number",`  
   	`"employment_details": "object",`  
   	`"credit_score": "number",`  
   	`"existing_obligations": "array"`  
 	`},`  
 	`"co_borrowers": ["object"],`  
 	`"guarantors": ["object"]`  
   `},`  
    
   `"lender_details": {`  
 	`"institution_name": "string",`  
 	`"institution_type": "bank|nbfc|housing_finance|cooperative",`  
 	`"license_number": "string",`  
 	`"registered_office": "object",`  
 	`"authorized_signatory": "object",`  
 	`"branch_details": "object"`  
   `},`  
    
   `"loan_terms": {`  
 	`"principal_details": {`  
   	`"sanctioned_amount": "number",`  
   	`"disbursement_schedule": "array",`  
   	`"loan_purpose": "string",`  
   	`"end_use_monitoring": "boolean"`  
 	`},`  
 	`"interest_structure": {`  
   	`"interest_rate_type": "fixed|floating|hybrid",`  
   	`"base_rate": "number",`  
   	`"spread_margin": "number",`  
   	`"current_rate": "number",`  
   	`"rate_reset_frequency": "monthly|quarterly|annually",`  
   	`"benchmark": "repo_rate|mclr|external_benchmark",`  
   	`"compounding_frequency": "monthly|quarterly|annually"`  
 	`},`  
 	`"tenure_details": {`  
   	`"loan_tenure_months": "number",`  
   	`"moratorium_period": "number",`  
   	`"prepayment_allowed": "boolean",`  
   	`"prepayment_charges": "object",`  
   	`"part_payment_facility": "boolean"`  
 	`}`  
   `},`  
    
   `"repayment_structure": {`  
 	`"repayment_method": "emi|bullet|step_up|step_down|seasonal",`  
 	`"emi_amount": "number",`  
 	`"repayment_frequency": "monthly|quarterly|annually",`  
 	`"repayment_start_date": "date",`  
 	`"repayment_mode": "ecs|nach|cheque|online",`  
 	`"bank_account_details": "object",`  
 	`"holiday_treatment": "object"`  
   `},`  
    
   `"charges_and_fees": {`  
     `"processing_fee": "number",`  
 	`"documentation_charges": "number",`  
 	`"valuation_charges": "number",`  
 	`"legal_charges": "number",`  
 	`"stamp_duty": "number",`  
 	`"insurance_premiums": "object",`  
 	`"penal_charges": {`  
   	`"overdue_interest_rate": "number",`  
   	`"bounce_charges": "number",`  
   	`"late_payment_penalty": "object"`  
 	`}`  
   `},`  
    
   `"security_details": {`  
 	`"primary_security": {`  
   	`"security_type": "mortgage|hypothecation|pledge|assignment",`  
   	`"asset_description": "object",`  
   	`"asset_valuation": "number",`  
   	`"valuation_date": "date",`  
   	`"loan_to_value_ratio": "number",`  
   	`"insurance_requirements": "object"`  
 	`},`  
 	`"collateral_security": ["object"],`  
 	`"guarantees": {`  
   	`"personal_guarantees": ["object"],`  
   	`"corporate_guarantees": ["object"],`  
   	`"bank_guarantees": ["object"]`  
 	`}`  
   `},`  
    
   `"financial_covenants": {`  
 	`"borrower_obligations": {`  
   	`"minimum_turnover": "number",`  
       `"debt_service_coverage_ratio": "number",`  
   	`"current_ratio_minimum": "number",`  
       `"debt_equity_ratio_maximum": "number",`  
       `"tangible_net_worth_minimum": "number"`  
 	`},`  
 	`"reporting_requirements": {`  
       `"financial_statements_frequency": "monthly|quarterly|annually",`  
   	`"audit_requirements": "boolean",`  
       `"compliance_certificates": "array",`  
   	`"stock_statements": "boolean"`  
 	`},`  
 	`"restrictive_covenants": {`  
       `"additional_borrowing_restrictions": "object",`  
       `"asset_disposal_restrictions": "object",`  
       `"change_in_management_restrictions": "object",`  
       `"dividend_payment_restrictions": "object"`  
 	`}`  
   `},`  
    
   `"default_and_recovery": {`  
 	`"events_of_default": [`  
   	`"non_payment_of_dues",`  
   	`"breach_of_covenants",`  
   	`"cross_default",`  
       `"material_adverse_change",`  
   	`"insolvency_proceedings"`  
 	`],`  
 	`"cure_period": "number",`  
 	`"acceleration_clause": "object",`  
 	`"recovery_mechanisms": {`  
   	`"sarfaesi_applicable": "boolean",`  
   	`"arbitration_clause": "boolean",`  
   	`"jurisdiction": "string",`  
   	`"asset_reconstruction": "boolean"`  
 	`}`  
   `}`  
 `}`

**3\. Terms of Service (Indian Context)**

**Legal Framework**

·       **Primary Legislation:** Information Technology Act, 2000; Consumer Protection Act, 2019

·       **Regulatory Bodies:** Ministry of Electronics & IT (MeitY), Competition Commission of India

·       **Key Rules:** IT (Intermediary Guidelines) Rules, 2021; Personal Data Protection Bill

·       **Sector-Specific:** RBI guidelines for fintech, SEBI for investment platforms

**Common Document Structure**

**Core Components**

1\.   	**Service Definition**

o   Platform/service description

o   User eligibility and registration

o   Account creation and verification

o   Service availability and limitations

2\.   	**User Rights and Obligations**

o   Acceptable use policies

o   Prohibited activities

o   Content guidelines and moderation

o   Intellectual property rights

3\.   	**Commercial Terms**

o   Pricing and payment terms

o   Subscription models

o   Refund and cancellation policies

o   Currency and tax implications

4\.  	**Platform Governance**

o   Service level agreements

o   Limitation of liability

o   Indemnification clauses

o   Dispute resolution mechanisms

**Terms of Service Schema (Indian Context)**

`{`  
   `"tos_metadata": {`  
 	`"service_provider": {`  
   	`"company_name": "string",`  
   	`"incorporation_details": "object",`  
   	`"registered_address": "object",`  
   	`"cin_number": "string",`  
   	`"gstin": "string",`  
   	`"contact_information": "object"`  
 	`},`  
 	`"document_details": {`  
   	`"version_number": "string",`  
   	`"effective_date": "date",`  
   	`"last_updated": "date",`  
   	`"supersedes_version": "string",`  
       `"applicable_jurisdiction": "india",`  
   	`"governing_state_laws": "string"`  
 	`}`  
   `},`  
     
   `"service_definition": {`  
 	`"platform_description": {`  
   	`"service_category": "digital_platform|mobile_app|web_service|saas|marketplace",`  
   	`"core_functionality": "string",`  
   	`"target_user_base": "b2c|b2b|b2b2c",`  
       `"geographic_availability": ["string"],`  
       `"minimum_age_requirement": "number",`  
   	`"kyc_requirements": "boolean"`  
 	`},`  
 	`"user_eligibility": {`  
       `"citizenship_requirements": "indian_residents|global|specific_countries",`  
   	`"age_restrictions": "object",`  
   	`"professional_requirements": "object",`  
   	`"verification_process": "object",`  
   	`"prohibited_users": ["string"]`  
 	`},`  
 	`"account_management": {`  
   	`"registration_process": "object",`  
       `"verification_requirements": "object",`  
   	`"account_types": ["string"],`  
   	`"suspension_grounds": ["string"],`  
       `"data_retention_post_closure": "object"`  
 	`}`  
   `},`  
    
   `"user_rights_obligations": {`  
 	`"user_rights": {`  
   	`"service_access_rights": "object",`  
   	`"data_portability": "boolean",`  
   	`"grievance_redressal": "object",`  
   	`"privacy_controls": "object",`  
   	`"content_ownership": "object"`  
 	`},`  
 	`"acceptable_use_policy": {`  
   	`"permitted_activities": ["string"],`  
   	`"prohibited_activities": [`  
     	`"illegal_content",`  
     	`"spam_activities",`  
         `"copyright_infringement",`  
     	`"harassment",`  
         `"fraudulent_transactions"`  
   	`],`  
   	`"content_guidelines": "object",`  
   	`"community_standards": "object"`  
 	`},`  
 	`"compliance_obligations": {`  
   	`"indian_law_compliance": "boolean",`  
   	`"tax_obligations": "object",`  
   	`"regulatory_reporting": "object",`  
   	`"data_localization": "boolean"`  
 	`}`  
   `},`  
    
   `"commercial_terms": {`  
 	`"pricing_structure": {`  
   	`"pricing_model": "free|freemium|subscription|transaction_based|usage_based",`  
   	`"base_charges": "number",`  
   	`"variable_charges": "object",`  
   	`"currency": "INR",`  
   	`"billing_cycle": "monthly|quarterly|annually|per_transaction",`  
   	`"price_change_policy": "object"`  
 	`},`  
 	`"payment_processing": {`  
   	`"accepted_payment_methods": ["string"],`  
       `"payment_gateway_partners": ["string"],`  
       `"auto_debit_authorization": "boolean",`  
       `"payment_security_standards": "pci_dss|iso27001",`  
   	`"transaction_limits": "object"`  
 	`},`  
 	`"refund_cancellation": {`  
   	`"refund_policy": "object",`  
   	`"cancellation_process": "object",`  
   	`"cooling_off_period": "number",`  
   	`"pro_rata_adjustments": "boolean",`  
       `"dispute_resolution_timeline": "number"`  
 	`},`  
 	`"taxation": {`  
   	`"gst_applicability": "boolean",`  
   	`"tds_implications": "object",`  
       `"foreign_exchange_compliance": "object",`  
   	`"tax_invoice_generation": "boolean"`  
 	`}`  
   `},`  
    
   `"platform_governance": {`  
 	`"service_availability": {`  
   	`"uptime_commitment": "number",`  
   	`"scheduled_maintenance": "object",`  
   	`"force_majeure_events": ["string"],`  
       `"service_discontinuation_notice": "number"`  
 	`},`  
 	`"content_moderation": {`  
   	`"moderation_policy": "object",`  
   	`"automated_filtering": "boolean",`  
   	`"human_review_process": "object",`  
   	`"appeal_mechanism": "object",`  
   	`"transparency_reporting": "boolean"`  
 	`},`  
 	`"intellectual_property": {`  
   	`"platform_ip_ownership": "object",`  
   	`"user_content_licensing": "object",`  
   	`"dmca_compliance": "boolean",`  
   	`"trademark_policy": "object",`  
   	`"third_party_ip_respect": "object"`  
 	`}`  
   `},`  
    
   `"liability_indemnification": {`  
 	`"limitation_of_liability": {`  
   	`"liability_cap": "number|unlimited|revenue_based",`  
   	`"excluded_damages": ["string"],`  
   	`"force_majeure_protection": "object",`  
   	`"third_party_claims": "object"`  
 	`},`  
 	`"indemnification": {`  
       `"user_indemnification_obligations": "object",`  
       `"platform_indemnification_scope": "object",`  
   	`"defense_obligations": "object",`  
   	`"settlement_authority": "object"`  
 	`},`  
 	`"insurance_coverage": {`  
   	`"professional_indemnity": "boolean",`  
   	`"cyber_liability": "boolean",`  
   	`"coverage_amounts": "object"`  
 	`}`  
   `},`  
    
   `"data_privacy": {`  
 	`"data_collection": {`  
   	`"personal_data_categories": ["string"],`  
   	`"collection_methods": ["string"],`  
   	`"legal_basis": "consent|contract|legitimate_interest|legal_obligation",`  
       `"third_party_data_sources": ["string"]`  
 	`},`  
 	`"data_processing": {`  
   	`"processing_purposes": ["string"],`  
   	`"data_sharing_practices": "object",`  
   	`"cross_border_transfers": "object",`  
   	`"retention_periods": "object",`  
       `"automated_decision_making": "boolean"`  
 	`},`  
 	`"user_controls": {`  
   	`"access_rights": "boolean",`  
   	`"correction_rights": "boolean",`  
   	`"deletion_rights": "boolean",`  
   	`"portability_rights": "boolean",`  
   	`"consent_withdrawal": "boolean"`  
 	`}`  
   `},`  
    
   `"dispute_resolution": {`  
 	`"grievance_mechanism": {`  
       `"internal_complaint_process": "object",`  
   	`"response_timeline": "number",`  
   	`"escalation_matrix": "object",`  
       `"grievance_officer_details": "object"`  
 	`},`  
 	`"legal_framework": {`  
   	`"governing_law": "indian_law",`  
   	`"jurisdiction": "string",`  
   	`"arbitration_clause": {`  
     	`"arbitration_mandatory": "boolean",`  
     	`"arbitration_seat": "string",`  
     	`"arbitration_rules": "string",`  
         `"number_of_arbitrators": "number"`  
   	`},`  
   	`"class_action_waiver": "boolean"`  
 	`},`  
     `"alternative_dispute_resolution": {`  
   	`"mediation_preference": "boolean",`  
       `"online_dispute_resolution": "boolean",`  
       `"sector_specific_ombudsman": "object"`  
 	`}`  
   `}`  
 `}`

**Cross-Document Analysis Patterns**

**Common Legal Elements Across All Three Document Types**

1\.   	**Party Identification and Verification**

o   PAN card requirements

o   Aadhaar linking mandates

o   Address verification protocols

o   Digital signature acceptance

2\.   	**Governing Law and Jurisdiction**

o   Indian law applicability

o   State-specific regulations

o   Court jurisdiction clauses

o   Alternative dispute resolution preferences

3\.   	**Financial Terms and Tax Implications**

o   GST applicability and compliance

o   TDS (Tax Deducted at Source) implications

o   Stamp duty requirements

o   Foreign exchange regulations (if applicable)

4\.  	**Termination and Exit Clauses**

o   Notice period requirements

o   Breach consequences

o   Asset return/settlement procedures

o   Post-termination obligations

**Risk Assessment Framework**

Each document type presents unique risk patterns that can be algorithmically identified:

**High-Risk Indicators**

·       **Rental Agreements:** Excessive security deposits, unfair termination clauses, maintenance cost shifting

·       **Loan Contracts:** High penalty rates, cross-default clauses, personal guarantee requirements

·       **Terms of Service:** Broad liability exclusions, unlimited data usage rights, unclear refund policies

**Compliance Red Flags**

·       Missing mandatory disclosures

·       Violation of consumer protection norms

·       Non-compliance with sector-specific regulations

·       Inadequate grievance redressal mechanisms
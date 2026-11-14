import subprocess

sql = """
UPDATE onboarding_progress 
SET status = 'approved',
    draft_blob = jsonb_set(
        jsonb_set(
            jsonb_set(
                draft_blob,
                '{kyc}',
                '{"verified": true, "pendingAdminReview": false, "rejectedByAdmin": false}'::jsonb,
                true
            ),
            '{step1,autoAccept}',
            'true'::jsonb,
            true
        ),
        '{payout}',
        '{"bankName": "ACB", "accountNumber": "2345678901", "accountHolder": "NGUYEN VAN SELLER MOT"}'::jsonb,
        true
    )
WHERE user_id = '942ce58d-da03-4848-97c3-669325e06177';
"""

proc = subprocess.run(
    'docker exec -i trustbase-postgres psql -U user -d trustbase',
    input=sql.encode('utf-8'),
    capture_output=True,
    shell=True
)

print('STDOUT:', proc.stdout.decode('utf-8', errors='ignore'))
print('STDERR:', proc.stderr.decode('utf-8', errors='ignore'))

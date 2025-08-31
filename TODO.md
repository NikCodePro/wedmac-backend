# TODO: Implement Capping System for Leads

## Steps to Complete

- [x] Update Lead Model: Add max_claims, claimed_artists, booked_artists, add 'booked' to STATUS_CHOICES
- [x] Modify ClaimLeadView: Update logic for many-to-many claims with capping
- [x] Create BookLeadView: New view for booking leads
- [x] Update GetMyClaimedLeadsView: Change filter to claimed_artists
- [x] Update Serializers: Add new fields and counts
- [x] Update Signals: Modify for new many-to-many fields
- [x] Create Migration: Generate and run for new fields
- [x] Test Changes: Verify functionality

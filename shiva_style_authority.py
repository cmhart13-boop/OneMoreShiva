"""Single owner switch for Shiva page-specific presentation.

The runtime shell owns app chrome/first paint. shiva_fixes owns the shared Home-based
presentation for Draft, Guide, Coach, and bottom navigation. Disable the older Guide
and Coach CSS payloads so those pages are not styled by multiple competing layers.
"""

import shiva_coach as _coach
import shiva_draft_guide as _guide

# Keep page behavior/content intact; disable only their legacy CSS injections.
_guide.CSS = ""
_coach.CSS = ""

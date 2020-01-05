**Added:**
 * code to give more feedback to the user when the builder fails due to a database error

**Changed:**
 * unsegregated expense can now tolerate "tbd".  This allows users to put a
   placeholder entry when the exact amount is not known, and then find it easily
   later.  Code flags all tbd entries at build time, but doesn't crash.

**Deprecated:** None

**Removed:** None

**Fixed:** None

**Security:** None

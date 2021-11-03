**Added:** None

**Changed:**
 * merge_collections_all returns all of two collections, where items dererenced
   are merged
 * merge_collections_intersect returns just merged items that are dereferenced
 * merge_collections_superior returns all except the non-dereferenced items in
   the inferior collection.  e.g., if we are merging grants and proposals and we
   want all grants, augmented by information in the proposals that led to those
   grants, we use this.

**Deprecated:** None

**Removed:** None

**Fixed:**
 * bug that person in two groups doesn't iterate over their proposals correctly
   in current-pending

**Security:** None
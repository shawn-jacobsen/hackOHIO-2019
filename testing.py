import mobikit

mobikit.set_api_key(373afebc8a2b2ee5d5e7743cc73565c82d9ecdd8)

dataframes = mobikit.workspaces.load(<work_space_id::int>, <feed_name::str?>, <query::object?>)
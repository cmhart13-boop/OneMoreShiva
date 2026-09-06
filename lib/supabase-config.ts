const fallbackUrl = 'https://wrhgxzweksizelffgcii.supabase.co'
const fallbackPublishableKey = 'sb_publishable_-8nGr9FwiqeJ4QpjuzmPDQ_4aiNC8Xb'

export function supabaseConfig() {
  const url = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL || fallbackUrl
  const key = process.env.SUPABASE_PUBLISHABLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY || fallbackPublishableKey
  return { url: url.replace(/\/$/, ''), key }
}

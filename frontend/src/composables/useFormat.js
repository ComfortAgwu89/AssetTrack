export function useFormat(currencySymbol = '₦') {
  const number = new Intl.NumberFormat('en-NG', { maximumFractionDigits: 0 })
  return {
    money: (value) => `${currencySymbol}${number.format(Math.round(value ?? 0))}`,
    // Compact form for cards: ₦1.2B, ₦340.5M
    moneyCompact: (value) => {
      const v = value ?? 0
      const abs = Math.abs(v)
      if (abs >= 1e9) return `${currencySymbol}${(v / 1e9).toFixed(2)}B`
      if (abs >= 1e6) return `${currencySymbol}${(v / 1e6).toFixed(1)}M`
      return `${currencySymbol}${number.format(Math.round(v))}`
    },
    count: (value) => number.format(value ?? 0),
    dateTime: (iso) =>
      iso ? new Date(iso).toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'short' }) : '',
  }
}

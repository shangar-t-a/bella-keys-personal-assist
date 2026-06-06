const INDIAN_RUPEE_FORMAT = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export const formatCurrency = (value: number): string => {
  return INDIAN_RUPEE_FORMAT.format(value);
};

export const formatCompactRupees = (value: number): string => {
  if (value === 0) return '₹0.00';
  const isNegative = value < 0;
  const absVal = Math.abs(value);
  let result = '';

  if (absVal >= 10000000) {
    result = `₹${(absVal / 10000000).toFixed(2)} Cr`;
  } else if (absVal >= 100000) {
    result = `₹${(absVal / 100000).toFixed(2)}L`;
  } else {
    result = formatCurrency(absVal);
    return isNegative ? `-${result}` : result;
  }
  
  return isNegative ? `-${result}` : result;
};

export const getMonthName = (monthIndex: number): string => {
  const date = new Date();
  date.setMonth(monthIndex);
  return date.toLocaleString('en-US', { month: 'long' });
};

export const getMonthIndex = (monthName: string): number => {
  return new Date(Date.parse(monthName + " 1, 2000")).getMonth();
};

export const formatMonthYear = (month: string, year: number): string => {
  const monthIndex = getMonthIndex(month);
  const date = new Date(year, monthIndex);
  return date.toLocaleString('en-US', { month: 'short', year: 'numeric' });
};

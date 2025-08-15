const INDIAN_RUPEE_FORMAT = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export const formatCurrency = (value: number): string => {
  return INDIAN_RUPEE_FORMAT.format(value);
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

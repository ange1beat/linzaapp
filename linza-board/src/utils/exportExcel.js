import * as XLSX from 'xlsx'

export function exportToExcel(detections, verifications) {
  const hasAnyConfirmed = Object.values(verifications).some(v => v === 'confirmed')

  const rows = detections
    .filter(d => {
      if (hasAnyConfirmed) {
        return verifications[d.id] === 'confirmed'
      }
      return true
    })
    .map((d, idx) => ({
      '№': idx + 1,
      'Тип нарушения': d.nameRu,
      'Временной интервал': d.timeInterval,
      'Категория': d.categoryLabel,
    }))

  if (rows.length === 0) {
    alert('Нет данных для экспорта')
    return
  }

  const ws = XLSX.utils.json_to_sheet(rows)

  ws['!cols'] = [
    { wch: 6 },
    { wch: 30 },
    { wch: 25 },
    { wch: 18 },
  ]

  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Нарушения')

  const today = new Date().toISOString().slice(0, 10)
  XLSX.writeFile(wb, `violations_report_${today}.xlsx`)
}

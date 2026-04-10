/**
 * Стартовый маршрут после входа и по клику «Главная» — совпадает с ролью портала.
 */
export function landingPathForPortalRole(r) {
  if (r === 'chief_editor') return '/editor/dashboard'
  if (r === 'administrator') return '/admin/wizard'
  if (r === 'lawyer') return '/lawyer/review'
  return '/files'
}

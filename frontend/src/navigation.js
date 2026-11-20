// Single source of truth for sidebar items and module routes.
// `stage` marks modules whose full screens arrive in a later development stage.
import {
  LayoutDashboard, Box, Tag, Building2, Users, ClipboardCheck, ArrowLeftRight, TrendingDown,
  Wrench, ListChecks, Trash2, FileText, History, UserCog, Settings,
} from 'lucide-vue-next'

export const navItems = [
  { name: 'dashboard', path: 'dashboard', label: 'Overview', icon: LayoutDashboard, perm: 'dashboard.view' },
  { name: 'assets', path: 'assets', label: 'Asset Register', icon: Box, perm: 'asset.view', stage: 2, blurb: 'Register, view, edit and archive assets with auto-generated asset numbers.' },
  { name: 'categories', path: 'categories', label: 'Categories', icon: Tag, perm: 'asset.view', stage: 2, blurb: 'Configure asset categories and their default depreciation settings.' },
  { name: 'departments', path: 'departments', label: 'Departments', icon: Building2, perm: 'asset.view', stage: 2, blurb: 'Manage departments and their locations.' },
  { name: 'custodians', path: 'custodians', label: 'Custodians', icon: Users, perm: 'asset.view', stage: 2, blurb: 'Manage the people accountable for assets.' },
  { name: 'assignments', path: 'assignments', label: 'Assignments', icon: ClipboardCheck, perm: 'asset.view', stage: 2, blurb: 'Assign assets, record acknowledgement of receipt and view custody history.' },
  { name: 'transfers', path: 'transfers', label: 'Transfers', icon: ArrowLeftRight, perm: 'asset.view', stage: 3, blurb: 'Request, approve and confirm transfers between departments, locations or custodians.' },
  { name: 'depreciation', path: 'depreciation', label: 'Depreciation', icon: TrendingDown, perm: 'depreciation.view', stage: 3, blurb: 'Depreciation schedules and posting for straight-line and reducing-balance assets.' },
  { name: 'maintenance', path: 'maintenance', label: 'Maintenance', icon: Wrench, perm: 'maintenance.report', stage: 3, blurb: 'Report faults, schedule repairs and track maintenance costs.' },
  { name: 'verification', path: 'verification', label: 'Verification', icon: ListChecks, perm: 'verification.perform', stage: 3, blurb: 'Physical verification lists and inspection results.' },
  { name: 'disposal', path: 'disposal', label: 'Disposal', icon: Trash2, perm: 'disposal.manage', stage: 3, blurb: 'Record disposals with gain or loss calculated from carrying amount.' },
  { name: 'reports', path: 'reports', label: 'Reports', icon: FileText, perm: 'report.view', stage: 4, blurb: 'Fixed asset register and other reports with PDF and Excel export.' },
  { name: 'audit', path: 'audit', label: 'Audit Trail', icon: History, perm: 'audit.view', stage: 4, blurb: 'A tamper-resistant history of who changed what, and when.' },
  { name: 'users', path: 'users', label: 'User Management', icon: UserCog, perm: 'user.manage', stage: 2, blurb: 'Create users and assign roles.' },
  { name: 'settings', path: 'settings', label: 'Settings', icon: Settings, perm: 'settings.manage', stage: 4, blurb: 'Organisation profile and currency settings.' },
]

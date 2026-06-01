import { useState, type ReactNode } from 'react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import {
    alpha,
    AppBar,
    Box,
    Collapse,
    Divider,
    Drawer,
    IconButton,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Toolbar,
    Tooltip,
    Typography,
    useMediaQuery,
    useTheme,
    Avatar,
    Menu as MuiMenu,
    MenuItem,
} from '@mui/material';
import {
    AutoAwesome as Sparkles,
    BarChart as BarChart3,
    CalendarMonth,
    Chat as MessageCircle,
    ChevronLeft,
    ChevronRight,
    CreditCard,
    DarkMode as Moon,
    ExpandLess,
    ExpandMore,
    Home,
    LightMode as Sun,
    Menu,
    AccountBalanceWallet,
    Settings as SettingsIcon,
    Logout as LogoutIcon,
} from '@mui/icons-material';
import { useThemeMode } from '@/theme/ThemeProvider';
import { getAvailableServices } from '@/config/features';
import { useAuth } from '@/context/AuthContext';

const DRAWER_WIDTH = 240;
const MINI_WIDTH = 64;

interface NavChild {
    name: string;
    href: string;
    icon: React.ElementType;
}

interface NavItem {
    name: string;
    href: string;
    icon: React.ElementType;
    exact?: boolean;
    children?: NavChild[];
}

interface NavSection {
    section: string;
    items: NavItem[];
}

// Get dynamic navigation sections based on available services
const getNavSections = (): NavSection[] => {
    const services = getAvailableServices();
    const sections: NavSection[] = [
        {
            section: 'Main',
            items: [{ name: 'Home', href: '/', icon: Home, exact: true }],
        },
    ];

    // Add Finance section if Expense Manager is enabled
    if (services.expenseManager) {
        sections.push({
            section: 'Finance',
            items: [
                {
                    name: 'Dashboard',
                    href: '/dashboard',
                    icon: BarChart3,
                    children: [
                        {
                            name: 'Account Balances',
                            href: '/dashboard/accounts',
                            icon: CreditCard,
                        },
                        {
                            name: 'Savings Envelopes',
                            href: '/dashboard/envelopes',
                            icon: AccountBalanceWallet,
                        },
                    ],
                },
                {
                    name: 'Monthly Budget',
                    href: '/budget',
                    icon: CalendarMonth,
                },
            ],
        });
    }

    // Add AI section if Bella Chat is enabled
    if (services.bellaChat) {
        sections.push({
            section: 'AI',
            items: [{ name: 'Bella Chat', href: '/chat', icon: MessageCircle }],
        });
    }

    return sections;
};

const LINK_STYLE = { textDecoration: 'none', color: 'inherit', display: 'block' } as const;

export default function AppShell({ children }: { children: ReactNode }) {
    const [open, setOpen] = useState(true);
    const [mobileOpen, setMobileOpen] = useState(false);
    const [expandedItems, setExpandedItems] = useState<Record<string, boolean>>({ Dashboard: true });
    const location = useLocation();
    const { mode, toggleTheme } = useThemeMode();
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('md'));
    const navSections = getNavSections();

    const { user, logout } = useAuth();
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const userMenuOpen = Boolean(anchorEl);
    
    const handleUserMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget);
    };
    
    const handleUserMenuClose = () => {
        setAnchorEl(null);
    };
    
    const handleLogout = () => {
        handleUserMenuClose();
        logout();
    };

    const isActive = (href: string, exact = false) =>
        exact
            ? location.pathname === href
            : location.pathname === href || location.pathname.startsWith(`${href}/`);

    const toggleExpand = (name: string) =>
        setExpandedItems((prev) => ({ ...prev, [name]: !prev[name] }));

    const closeMobile = () => setMobileOpen(false);

    const brandGradient = `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`;

    const BrandLogo = ({ size = 30 }: { size?: number }) => (
        <Box
            sx={{
                width: size,
                height: size,
                borderRadius: 1.5,
                background: brandGradient,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
            }}
        >
            <Sparkles sx={{ color: 'white', fontSize: size * 0.5 }} />
        </Box>
    );

    const sidebarContent = (mobile: boolean) => {
        const isOpen = open || mobile;

        return (
            <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', userSelect: 'none' }}>
                {/* ── Header ─────────────────────────────────────── */}
                <Box
                    sx={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: isOpen ? 'space-between' : 'center',
                        px: isOpen ? 1.5 : 1,
                        minHeight: 56,
                        flexShrink: 0,
                    }}
                >
                    {isOpen && (
                        <RouterLink
                            to="/"
                            style={{ ...LINK_STYLE, display: 'flex', alignItems: 'center', gap: 10 }}
                            onClick={mobile ? closeMobile : undefined}
                        >
                            <BrandLogo />
                            <Typography
                                variant="subtitle2"
                                sx={{
                                    fontWeight: 700,
                                    fontFamily: '"Space Grotesk", sans-serif',
                                    background: brandGradient,
                                    backgroundClip: 'text',
                                    WebkitBackgroundClip: 'text',
                                    WebkitTextFillColor: 'transparent',
                                    whiteSpace: 'nowrap',
                                }}
                            >
                                Bella
                            </Typography>
                        </RouterLink>
                    )}

                    {!isOpen && <BrandLogo />}

                    <Tooltip
                        title={mobile ? 'Close' : open ? 'Collapse' : 'Expand'}
                        placement="right"
                    >
                        <IconButton
                            size="small"
                            onClick={mobile ? closeMobile : () => setOpen((v) => !v)}
                            sx={{ ml: isOpen ? 0.5 : 0 }}
                        >
                            {mobile || open ? (
                                <ChevronLeft fontSize="small" />
                            ) : (
                                <ChevronRight fontSize="small" />
                            )}
                        </IconButton>
                    </Tooltip>
                </Box>

                <Divider />

                {/* ── Navigation ─────────────────────────────────── */}
                <Box sx={{ flexGrow: 1, overflowY: 'auto', overflowX: 'hidden', py: 1 }}>
                    {navSections.map((section, idx) => (
                        <Box key={section.section}>
                            {isOpen ? (
                                <Typography
                                    variant="caption"
                                    sx={{
                                        px: 2.5,
                                        pt: idx > 0 ? 2 : 1,
                                        pb: 0.5,
                                        display: 'block',
                                        color: 'text.disabled',
                                        fontWeight: 700,
                                        textTransform: 'uppercase',
                                        letterSpacing: '0.08em',
                                        fontSize: '0.625rem',
                                    }}
                                >
                                    {section.section}
                                </Typography>
                            ) : (
                                idx > 0 && <Divider sx={{ my: 1, mx: 1.5 }} />
                            )}

                            <List disablePadding dense>
                                {section.items.map((item) => {
                                    const Icon = item.icon;
                                    const hasChildren = !!item.children?.length;
                                    const active = hasChildren
                                        ? item.children!.some(child => isActive(child.href, true))
                                        : isActive(item.href, item.exact);
                                    const childExpanded = expandedItems[item.name];

                                    const activeStyle = active
                                        ? {
                                            bgcolor: alpha(theme.palette.primary.main, 0.1),
                                            color: theme.palette.primary.main,
                                            '&::before': {
                                                content: '""',
                                                position: 'absolute',
                                                left: 0,
                                                top: '20%',
                                                height: '60%',
                                                width: 3,
                                                bgcolor: 'primary.main',
                                                borderRadius: '0 3px 3px 0',
                                            },
                                        }
                                        : {};

                                    const btn = (
                                        <ListItemButton
                                            onClick={hasChildren ? () => toggleExpand(item.name) : undefined}
                                            sx={{
                                                borderRadius: 1.5,
                                                py: 0.875,
                                                minHeight: 40,
                                                position: 'relative',
                                                ...(isOpen
                                                    ? activeStyle
                                                    : active
                                                        ? { bgcolor: alpha(theme.palette.primary.main, 0.1), color: theme.palette.primary.main }
                                                        : {}),
                                                '&:hover': { bgcolor: alpha(theme.palette.primary.main, 0.06) },
                                                ...(isOpen ? {} : { justifyContent: 'center' }),
                                            }}
                                        >
                                            <ListItemIcon
                                                sx={{
                                                    minWidth: isOpen ? 36 : 0,
                                                    color: active ? 'primary.main' : 'text.secondary',
                                                    justifyContent: 'center',
                                                }}
                                            >
                                                <Icon sx={{ fontSize: 20 }} />
                                            </ListItemIcon>
                                            {isOpen && (
                                                <>
                                                    <ListItemText
                                                        primary={item.name}
                                                        primaryTypographyProps={{
                                                            fontSize: '0.875rem',
                                                            fontWeight: active ? 600 : 400,
                                                        }}
                                                    />
                                                    {hasChildren &&
                                                        (childExpanded ? (
                                                            <ExpandLess fontSize="small" />
                                                        ) : (
                                                            <ExpandMore fontSize="small" />
                                                        ))}
                                                </>
                                            )}
                                        </ListItemButton>
                                    );

                                    return (
                                        <Box key={item.name}>
                                            <ListItem disablePadding sx={{ px: 1, mb: 0.25 }}>
                                                {!isOpen ? (
                                                    <Tooltip title={item.name} placement="right">
                                                        <Box sx={{ width: '100%' }}>
                                                            {hasChildren ? (
                                                                btn
                                                            ) : (
                                                                <RouterLink
                                                                    to={item.href}
                                                                    style={LINK_STYLE}
                                                                >
                                                                    {btn}
                                                                </RouterLink>
                                                            )}
                                                        </Box>
                                                    </Tooltip>
                                                ) : hasChildren ? (
                                                    btn
                                                ) : (
                                                    <RouterLink
                                                        to={item.href}
                                                        style={{ ...LINK_STYLE, width: '100%' }}
                                                        onClick={mobile ? closeMobile : undefined}
                                                    >
                                                        {btn}
                                                    </RouterLink>
                                                )}
                                            </ListItem>

                                            {/* Sub-items */}
                                            {hasChildren && isOpen && (
                                                <Collapse in={childExpanded} timeout="auto">
                                                    <List disablePadding dense>
                                                        {item.children!.map((child) => {
                                                            const ChildIcon = child.icon;
                                                            const childActive = isActive(child.href, true);
                                                            return (
                                                                <ListItem
                                                                    key={child.href}
                                                                    disablePadding
                                                                    sx={{ pl: 2.5, pr: 1, mb: 0.25 }}
                                                                >
                                                                    <RouterLink
                                                                        to={child.href}
                                                                        style={{ ...LINK_STYLE, width: '100%' }}
                                                                        onClick={mobile ? closeMobile : undefined}
                                                                    >
                                                                        <ListItemButton
                                                                            sx={{
                                                                                borderRadius: 1.5,
                                                                                py: 0.625,
                                                                                minHeight: 36,
                                                                                color: childActive
                                                                                    ? 'secondary.main'
                                                                                    : 'text.secondary',
                                                                                ...(childActive && {
                                                                                    bgcolor: alpha(theme.palette.secondary.main, 0.08),
                                                                                }),
                                                                                '&:hover': {
                                                                                    bgcolor: alpha(theme.palette.secondary.main, 0.06),
                                                                                },
                                                                            }}
                                                                        >
                                                                            <ListItemIcon
                                                                                sx={{
                                                                                    minWidth: 30,
                                                                                    color: childActive ? 'secondary.main' : 'text.disabled',
                                                                                }}
                                                                            >
                                                                                <ChildIcon sx={{ fontSize: 16 }} />
                                                                            </ListItemIcon>
                                                                            <ListItemText
                                                                                primary={child.name}
                                                                                primaryTypographyProps={{
                                                                                    fontSize: '0.8125rem',
                                                                                    fontWeight: childActive ? 600 : 400,
                                                                                }}
                                                                            />
                                                                        </ListItemButton>
                                                                    </RouterLink>
                                                                </ListItem>
                                                            );
                                                        })}
                                                    </List>
                                                </Collapse>
                                            )}
                                        </Box>
                                    );
                                })}
                            </List>
                        </Box>
                    ))}
                </Box>

                <Divider />

                {/* ── User Profile ───────────────────────────────── */}
                <Box sx={{ px: 1, py: 0.5 }}>
                    {isOpen ? (
                        <ListItemButton
                            onClick={handleUserMenuOpen}
                            sx={{
                                borderRadius: 1.5,
                                py: 0.75,
                                px: 1.5,
                                minHeight: 48,
                                display: 'flex',
                                alignItems: 'center',
                                gap: 1.5,
                                '&:hover': { bgcolor: alpha(theme.palette.primary.main, 0.06) },
                            }}
                        >
                            <Avatar
                                sx={{
                                    width: 32,
                                    height: 32,
                                    bgcolor: theme.palette.primary.main,
                                    fontSize: '0.875rem',
                                    fontWeight: 600,
                                }}
                            >
                                {user?.username ? user.username[0].toUpperCase() : 'U'}
                            </Avatar>
                            <Box sx={{ minWidth: 0, flexGrow: 1, textAlign: 'left' }}>
                                <Typography
                                    variant="subtitle2"
                                    noWrap
                                    sx={{
                                        fontWeight: 600,
                                        fontSize: '0.875rem',
                                        color: 'text.primary',
                                    }}
                                >
                                    {user?.username || 'Guest'}
                                </Typography>
                                <Typography
                                    variant="caption"
                                    noWrap
                                    sx={{
                                        display: 'block',
                                        color: 'text.secondary',
                                        fontSize: '0.75rem',
                                    }}
                                >
                                    {user?.role ? user.role.charAt(0).toUpperCase() + user.role.slice(1) : 'User'}
                                </Typography>
                            </Box>
                        </ListItemButton>
                    ) : (
                        <Tooltip title={user?.username || 'User Profile'} placement="right">
                            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                                <IconButton
                                    onClick={handleUserMenuOpen}
                                    size="small"
                                    sx={{
                                        p: 0.5,
                                        '&:hover': { bgcolor: alpha(theme.palette.primary.main, 0.06) },
                                    }}
                                >
                                    <Avatar
                                        sx={{
                                            width: 32,
                                            height: 32,
                                            bgcolor: theme.palette.primary.main,
                                            fontSize: '0.875rem',
                                            fontWeight: 600,
                                        }}
                                    >
                                        {user?.username ? user.username[0].toUpperCase() : 'U'}
                                    </Avatar>
                                </IconButton>
                            </Box>
                        </Tooltip>
                    )}
                </Box>

                <Divider />

                {/* ── Settings ───────────────────────────────────── */}
                <Box sx={{ px: 1, pt: 1, pb: 0.5 }}>
                    {isOpen ? (
                        <RouterLink to="/settings" style={LINK_STYLE} onClick={mobile ? closeMobile : undefined}>
                            <ListItemButton
                                sx={{
                                    borderRadius: 1.5,
                                    py: 0.875,
                                    minHeight: 40,
                                    position: 'relative',
                                    ...(isActive('/settings') ? {
                                        bgcolor: alpha(theme.palette.primary.main, 0.1),
                                        color: theme.palette.primary.main,
                                        '&::before': {
                                            content: '""',
                                            position: 'absolute',
                                            left: 0,
                                            top: '20%',
                                            height: '60%',
                                            width: 3,
                                            bgcolor: 'primary.main',
                                            borderRadius: '0 3px 3px 0',
                                        },
                                    } : {}),
                                    '&:hover': { bgcolor: alpha(theme.palette.primary.main, 0.06) },
                                }}
                            >
                                <ListItemIcon sx={{ minWidth: 36, color: isActive('/settings') ? 'primary.main' : 'text.secondary' }}>
                                    <SettingsIcon sx={{ fontSize: 20 }} />
                                </ListItemIcon>
                                <ListItemText
                                    primary="Settings"
                                    primaryTypographyProps={{
                                        fontSize: '0.875rem',
                                        fontWeight: isActive('/settings') ? 600 : 400,
                                    }}
                                />
                            </ListItemButton>
                        </RouterLink>
                    ) : (
                        <Tooltip title="Settings" placement="right">
                            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                                <RouterLink to="/settings" style={LINK_STYLE}>
                                    <IconButton
                                        size="small"
                                        color={isActive('/settings') ? 'primary' : 'default'}
                                        sx={{
                                            color: isActive('/settings') ? 'primary.main' : 'text.secondary',
                                            bgcolor: isActive('/settings') ? alpha(theme.palette.primary.main, 0.1) : 'transparent',
                                            '&:hover': { bgcolor: alpha(theme.palette.primary.main, 0.06) },
                                        }}
                                    >
                                        <SettingsIcon />
                                    </IconButton>
                                </RouterLink>
                            </Box>
                        </Tooltip>
                    )}
                </Box>

                {/* ── Theme toggle ───────────────────────────────── */}
                <Box sx={{ px: 1, pb: 1, pt: 0.5 }}>
                    {isOpen ? (
                        <ListItemButton onClick={toggleTheme} sx={{ borderRadius: 1.5, py: 0.875 }}>
                            <ListItemIcon sx={{ minWidth: 36 }}>
                                {mode === 'dark' ? <Sun sx={{ fontSize: 20 }} /> : <Moon sx={{ fontSize: 20 }} />}
                            </ListItemIcon>
                            <ListItemText
                                primary={mode === 'dark' ? 'Light Mode' : 'Dark Mode'}
                                primaryTypographyProps={{ fontSize: '0.875rem' }}
                            />
                        </ListItemButton>
                    ) : (
                        <Tooltip title={mode === 'dark' ? 'Light Mode' : 'Dark Mode'} placement="right">
                            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                                <IconButton size="small" onClick={toggleTheme}>
                                    {mode === 'dark' ? <Sun /> : <Moon />}
                                </IconButton>
                            </Box>
                        </Tooltip>
                    )}
                </Box>
            </Box>
        );
    };

    const permanentDrawerSx = {
        width: open ? DRAWER_WIDTH : MINI_WIDTH,
        flexShrink: 0,
        transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: open
                ? theme.transitions.duration.enteringScreen
                : theme.transitions.duration.leavingScreen,
        }),
        '& .MuiDrawer-paper': {
            width: open ? DRAWER_WIDTH : MINI_WIDTH,
            boxSizing: 'border-box',
            overflowX: 'hidden',
            transition: theme.transitions.create('width', {
                easing: theme.transitions.easing.sharp,
                duration: open
                    ? theme.transitions.duration.enteringScreen
                    : theme.transitions.duration.leavingScreen,
            }),
        },
    };

    return (
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
            {/* Desktop permanent sidebar */}
            {!isMobile && (
                <Drawer variant="permanent" sx={permanentDrawerSx}>
                    {sidebarContent(false)}
                </Drawer>
            )}

            {/* Mobile overlay drawer */}
            <Drawer
                variant="temporary"
                open={mobileOpen}
                onClose={closeMobile}
                ModalProps={{ keepMounted: true }}
                sx={{
                    display: { xs: 'block', md: 'none' },
                    '& .MuiDrawer-paper': { width: DRAWER_WIDTH, boxSizing: 'border-box' },
                }}
            >
                {sidebarContent(true)}
            </Drawer>

            {/* Main content column */}
            <Box component="main" sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
                {/* Mobile-only top bar */}
                {isMobile && (
                    <AppBar
                        position="sticky"
                        elevation={0}
                        color="default"
                        sx={{ bgcolor: 'background.paper', borderBottom: `1px solid ${theme.palette.divider}` }}
                    >
                        <Toolbar variant="dense">
                            <IconButton edge="start" size="small" onClick={() => setMobileOpen(true)} sx={{ mr: 1.5 }}>
                                <Menu />
                            </IconButton>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <BrandLogo size={24} />
                                <Typography
                                    variant="subtitle2"
                                    sx={{
                                        fontWeight: 700,
                                        fontFamily: '"Space Grotesk", sans-serif',
                                        background: brandGradient,
                                        backgroundClip: 'text',
                                        WebkitBackgroundClip: 'text',
                                        WebkitTextFillColor: 'transparent',
                                    }}
                                >
                                    Bella (Keys' Assist)
                                </Typography>
                            </Box>
                        </Toolbar>
                    </AppBar>
                )}

                {/* Page routes */}
                {children}
            </Box>

            {/* User Dropdown Menu */}
            <MuiMenu
                anchorEl={anchorEl}
                open={userMenuOpen}
                onClose={handleUserMenuClose}
                onClick={handleUserMenuClose}
                PaperProps={{
                    elevation: 3,
                    sx: {
                        overflow: 'visible',
                        filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.12))',
                        mt: 1,
                        minWidth: 180,
                        border: `1px solid ${theme.palette.divider}`,
                    },
                }}
                anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
                transformOrigin={{ vertical: 'bottom', horizontal: 'left' }}
            >
                <Box sx={{ px: 2, py: 1.5 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        {user?.username || 'Guest'}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                        {user?.role ? user.role.charAt(0).toUpperCase() + user.role.slice(1) : 'User'}
                    </Typography>
                </Box>
                <Divider />
                <MenuItem onClick={handleLogout} sx={{ gap: 1.5, py: 1 }}>
                    <LogoutIcon fontSize="small" color="action" />
                    <ListItemText primary="Log Out" primaryTypographyProps={{ fontSize: '0.875rem' }} />
                </MenuItem>
            </MuiMenu>
        </Box>
    );
}

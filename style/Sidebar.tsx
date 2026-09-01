import { NavLink } from 'react-router-dom';
import { useNotifications } from '@/hooks/useNotifications';
import { useRole, ROLE_CONFIG } from '@/contexts/RoleContext';
import ContactSuperiorPanel from './ContactSuperiorPanel';
import AvatarPhoto from '@/components/base/AvatarPhoto';
import { getPhotoUrl } from '@/config/userPhotos';

export default function Sidebar() {
  const { totalUnread } = useNotifications();
  const { navItems, displayName, config } = useRole();

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 flex flex-col z-30" style={{ background: 'linear-gradient(180deg, #002952 0%, #001429 100%)' }}>
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-white/10">
        <div className="w-9 h-9 flex items-center justify-center flex-shrink-0">
          <img
            src="https://static.readdy.ai/image/a02549f1fd3e2ac81d1fab65a599c074/79092b728ac3cc61e456b4699b8de52d.png"
            alt="NomiSystem Logo"
            className="w-9 h-9 object-contain"
          />
        </div>
        <div>
          <div className="text-white font-bold text-sm leading-tight">NomiSystem</div>
          <div className="text-white/50 text-xs">WorkHub</div>
        </div>
      </div>

      {/* User info */}
      <div className="flex items-center gap-3 px-5 py-4 border-b border-white/10">
        <AvatarPhoto
          name={displayName.name}
          size={32}
          borderColor="rgba(255,255,255,0.2)"
        />
        <div className="min-w-0">
          <div className="text-white text-xs font-medium truncate">{displayName.name}</div>
          <div className="text-white/40 text-xs truncate">{displayName.role}</div>
        </div>
        <div className="w-2 h-2 rounded-full bg-green-400 flex-shrink-0 ml-auto"></div>
      </div>

      {/* Role badge */}
      <div className="px-5 py-2 border-b border-white/10">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold" style={{ background: `${config.color}20`, color: config.color, border: `1px solid ${config.color}30` }}>
          <i className={`${config.icon} text-xs`}></i>
          {config.label}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 overflow-y-auto">
        <div className="text-white/30 text-xs font-semibold uppercase tracking-wider px-3 mb-2">Principal</div>
        <ul className="space-y-1">
          {navItems.map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                end={item.path === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-all duration-200 sidebar-item ${isActive ? 'sidebar-item-active' : ''}`
                }
              >
                {({ isActive }) => (
                  <>
                    <div className="w-5 h-5 flex items-center justify-center flex-shrink-0">
                      <i className={`${item.icon} text-base ${isActive ? 'text-[#51b1db]' : 'text-white/70'}`}></i>
                    </div>
                    <span className={`text-sm font-medium flex-1 ${isActive ? 'text-white' : 'text-white/70'}`}>{item.label}</span>
                    {item.dynamicBadge === 'chat' && totalUnread > 0 && (
                      <span className="text-xs font-bold px-1.5 py-0.5 rounded-full text-white animate-pulse" style={{ background: '#c60b44', minWidth: '20px', textAlign: 'center' }}>
                        {totalUnread}
                      </span>
                    )}
                    {!item.dynamicBadge && item.badge && (
                      <span className="text-xs font-bold px-1.5 py-0.5 rounded-full text-white" style={{ background: '#c60b44', minWidth: '20px', textAlign: 'center' }}>
                        {item.badge}
                      </span>
                    )}
                  </>
                )}
              </NavLink>
            </li>
          ))}
        </ul>

        {/* Contacto al superior */}
        <div className="mt-4 px-3">
          <ContactSuperiorPanel />
        </div>

        <div className="text-white/30 text-xs font-semibold uppercase tracking-wider px-3 mb-2 mt-6">Sistema</div>
        <ul className="space-y-1">
          <li>
            <button className="flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-all duration-200 sidebar-item w-full text-left">
              <div className="w-5 h-5 flex items-center justify-center flex-shrink-0">
                <i className="ri-settings-3-line text-base text-white/70"></i>
              </div>
              <span className="text-sm font-medium text-white/70">Configuración</span>
            </button>
          </li>
          <li>
            <button className="flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-all duration-200 sidebar-item w-full text-left">
              <div className="w-5 h-5 flex items-center justify-center flex-shrink-0">
                <i className="ri-question-line text-base text-white/70"></i>
              </div>
              <span className="text-sm font-medium text-white/70">Ayuda</span>
            </button>
          </li>
        </ul>
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-white/10">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-400"></div>
          <span className="text-white/40 text-xs">Sistema operativo</span>
        </div>
        <div className="text-white/20 text-xs mt-1">v2.4.1 · NomiSystem WorkHub</div>
      </div>
    </aside>
  );
}
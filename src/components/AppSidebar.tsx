import { NavLink } from "react-router-dom";
import { 
  LayoutDashboard, 
  Syringe,
  Package,
  AlertTriangle, 
  Database, 
  MessageSquare, 
  Info 
} from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";

const menuItems = [
  { title: "Dashboard Geral", url: "/", icon: LayoutDashboard },
  { title: "Aplicação", url: "/aplicacao", icon: Syringe },
  { title: "Distribuição", url: "/distribuicao", icon: Package },
  { title: "Qualidade dos Dados", url: "/qualidade", icon: Database },
  { title: "Sobre", url: "/sobre", icon: Info },
];

export function AppSidebar() {
  const { open } = useSidebar();

  return (
    <Sidebar className="border-r border-sidebar-border">
      <SidebarContent>
        <div className="px-4 py-6">
          <h1 className={`font-bold ${open ? 'text-xl' : 'text-sm text-center'} text-sidebar-foreground`}>
            {open ? 'Vacinação Brasil' : 'VB'}
          </h1>
          {open && <p className="text-xs text-sidebar-foreground/70 mt-1">2020–2024</p>}
        </div>
        
        <SidebarGroup>
          <SidebarGroupLabel className="text-sidebar-foreground/70">Navegação</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <NavLink
                      to={item.url}
                      end={item.url === "/"}
                      className={({ isActive }) =>
                        `flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                          isActive
                            ? "bg-sidebar-primary text-sidebar-primary-foreground font-medium"
                            : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                        }`
                      }
                    >
                      <item.icon className="h-4 w-4 flex-shrink-0" />
                      {open && <span className="text-sm">{item.title}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}

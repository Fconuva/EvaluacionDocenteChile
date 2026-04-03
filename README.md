# Evaluación Docente Chile - Agente Portafolios

Sistema de generación automatizada de portafolios para la **Evaluación DocenteMás Chile 2026**.

## Estructura

`
.claude/agents/Portafolios.agent.md    # Agente IA especializado en portafolios
Manuales/
  DOCUMENTACION/extracted/
    KNOWLEDGE_BASE.md                  # Base de conocimiento completa (rúbricas, criterios)
    *.txt                              # Textos extraídos de manuales y rúbricas oficiales
  ejemplos de portafolios 2025/        # Portafolios de ejemplo (HTML)
  CLIENTES/                            # [NO en repo - datos sensibles]
export_firebase.py                     # Script para exportar datos de docentes desde Firebase
`

## Uso

### 1. Exportar datos de docentes
`ash
python export_firebase.py EMAIL PASSWORD
`
Esto crea carpetas individuales en `Manuales/CLIENTES/` con el contexto de cada docente.

### 2. Generar portafolios
Usar el agente `Portafolios` en VS Code (Copilot Chat) con el contexto del docente.

## Niveles soportados
- Educación Básica Generalista (1° a 6°)
- Educación Básica por Asignaturas (5° y 6°)
- 7° Básico a 4° Medio
- Educación Media Técnico-Profesional
- Educación Parvularia
- Educación Especial
- Educación de Personas Jóvenes y Adultas (EPJA)

## Propiedad
Prof. Francisco Javier Núñez Valenzuela
www.profefranciscopancho.com

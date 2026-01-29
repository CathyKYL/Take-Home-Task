# Audit Trail PDF Generator
# Creates professional PDF reports of processing audit trails

import io
from datetime import datetime
from typing import List, Dict, Any, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas


class AuditTrailPDF:
    """Generate professional PDF audit trail reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles for the report"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#666666'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Info text style
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#555555'),
            spaceAfter=8,
            fontName='Helvetica'
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#999999'),
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        ))
    
    def _add_header_footer(self, canvas_obj, doc):
        """Add header and footer to each page"""
        canvas_obj.saveState()
        
        # Footer
        footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        canvas_obj.setFont('Helvetica-Oblique', 8)
        canvas_obj.setFillColor(colors.HexColor('#999999'))
        canvas_obj.drawCentredString(
            doc.pagesize[0] / 2,
            0.5 * inch,
            footer_text
        )
        
        # Page number
        page_num = canvas_obj.getPageNumber()
        canvas_obj.drawRightString(
            doc.pagesize[0] - 0.75 * inch,
            0.5 * inch,
            f"Page {page_num}"
        )
        
        canvas_obj.restoreState()
    
    def generate(
        self,
        run_id: str,
        audit_entries: List[Dict[str, Any]],
        run_summary: Optional[Dict[str, Any]] = None,
        upload_date: Optional[str] = None
    ) -> bytes:
        """
        Generate audit trail PDF report.
        
        Args:
            run_id: UUID of the processing run
            audit_entries: List of audit trail entries
            run_summary: Optional run summary with statistics
            upload_date: Optional upload date string
            
        Returns:
            bytes: PDF file content
        """
        # Create PDF in memory
        buffer = io.BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=1*inch,
            title=f"Audit Trail Report - {run_id}"
        )
        
        # Container for PDF elements
        story = []
        
        # Title
        title = Paragraph("Processing Audit Trail Report", self.styles['CustomTitle'])
        story.append(title)
        
        # Subtitle
        subtitle_text = "Complete log of all processing actions"
        subtitle = Paragraph(subtitle_text, self.styles['CustomSubtitle'])
        story.append(subtitle)
        story.append(Spacer(1, 0.3*inch))
        
        # Run Information Section
        story.append(Paragraph("Run Information", self.styles['SectionHeader']))
        
        run_info_data = [
            ["Run ID:", run_id],
            ["Generated:", datetime.now().strftime('%B %d, %Y at %I:%M %p')],
        ]
        
        if upload_date:
            run_info_data.append(["Upload Date:", upload_date])
        
        if run_summary:
            run_info_data.extend([
                ["Total Transactions:", str(run_summary.get('total_raw_rows', 'N/A'))],
                ["Ready to Pay:", str(run_summary.get('ready_to_pay_rows', 'N/A'))],
                ["Payment on Hold:", str(run_summary.get('payment_on_hold_rows', 'N/A'))],
                ["Reconciliation:", "✓ Passed" if run_summary.get('reconciliation_valid') else "✗ Failed"]
            ])
        
        run_info_table = Table(run_info_data, colWidths=[1.5*inch, 4.5*inch])
        run_info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#555555')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(run_info_table)
        story.append(Spacer(1, 0.4*inch))
        
        # Audit Trail Section
        story.append(Paragraph(
            f"Audit Trail ({len(audit_entries)} entries)",
            self.styles['SectionHeader']
        ))
        
        story.append(Paragraph(
            "All processing actions and overrides applied",
            self.styles['InfoText']
        ))
        story.append(Spacer(1, 0.2*inch))
        
        # Audit Trail Table
        audit_table_data = [
            ['Timestamp', 'Action', 'Details', 'Rows\nAffected']
        ]
        
        for entry in audit_entries:
            # Format timestamp
            timestamp_str = entry.get('timestamp', '')
            try:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                formatted_time = dt.strftime('%b %d, %I:%M:%S %p')
            except:
                formatted_time = timestamp_str[:19] if len(timestamp_str) >= 19 else timestamp_str
            
            # Get action
            action = entry.get('action', 'N/A')
            
            # Get details (wrap long text)
            details = entry.get('details', 'N/A')
            if len(details) > 60:
                details = details[:57] + '...'
            
            # Get rows affected
            rows_affected = entry.get('rows_affected')
            rows_str = str(rows_affected) if rows_affected is not None else '-'
            
            audit_table_data.append([
                formatted_time,
                action,
                details,
                rows_str
            ])
        
        # Create table with appropriate column widths
        audit_table = Table(
            audit_table_data,
            colWidths=[1.4*inch, 1.3*inch, 3*inch, 0.8*inch]
        )
        
        # Style the audit table
        audit_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 1), (-1, -1), 6),
            ('RIGHTPADDING', (0, 1), (-1, -1), 6),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        
        story.append(audit_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Data Integrity Statement
        story.append(Paragraph("Data Integrity Statement", self.styles['SectionHeader']))
        
        integrity_text = (
            "This audit trail shows all actions taken during processing, including manual mappings and overrides. "
            "No raw data was modified - all changes were applied as processing rules. "
            "Only 'Created Date' and 'Last Modified Date' columns were stamped in the output files."
        )
        story.append(Paragraph(integrity_text, self.styles['InfoText']))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes


def generate_audit_trail_pdf(
    run_id: str,
    audit_entries: List[Dict[str, Any]],
    run_summary: Optional[Dict[str, Any]] = None,
    upload_date: Optional[str] = None
) -> bytes:
    """
    Convenience function to generate audit trail PDF.
    
    Args:
        run_id: UUID of the processing run
        audit_entries: List of audit trail entries
        run_summary: Optional run summary with statistics
        upload_date: Optional upload date string
        
    Returns:
        bytes: PDF file content
    """
    generator = AuditTrailPDF()
    return generator.generate(
        run_id=run_id,
        audit_entries=audit_entries,
        run_summary=run_summary,
        upload_date=upload_date
    )


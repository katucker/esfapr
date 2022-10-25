# -*- coding: utf-8 -*-
"""
Created on Tue Aug 214 15:31:45 2022

@author: Keith.Tucker

Python class for generating an Annual Performance Report
(APR) for a Governor's Emergency Education Relief (GEER) Fund grant.

"""

from datetime import datetime
import logging
from typing import List

from dataclasses import dataclass

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.units import inch

ISO="Keith Tucker"

@dataclass
class GEER_Grantee:
    stateCode: str
    pk: str
    sk: str
    prNumber: str
    lastModifiedBy: str
    lastModifiedDate: datetime
    submittedBy: str
    submittedDate: datetime
    reportingYear: str
    granteeName: str
    repName: str
    repPosition: str
    repOffice: str
    repMailingAddress: str
    repPhone: str
    repEmail: str
    grantAmountAllocated: float
    grantAmountExpended: float
    awardedAmount_sub: float
    awardedAmount_sub_FLAG: str
    areLeasAwardedGeerFunds: bool
    areLeasAwardedGeerFunds_FLAG: str
    areIhesAwardedGeerFunds: bool
    areIhesAwardedGeerFunds_FLAG: str
    areEntitiesAwardedGeerFunds: bool
    areEntitiesAwardedGeerFunds_FLAG: str
    wereAnyConditionsPlacedByStateForLeaFunds: bool
    isStateLeaGeerAwardConditionChanges: bool
    stateLeaGeerAwardConditionChanges: str
    didStatePlaceDistanceLearningConditionsOnLeas: bool
    isSupportTechInfrastructureForLeaDistanceLearning: bool
    isInternetAccessNeededForLeas: bool
    areDevicesNeededForLeas: bool
    isTrainingStaffNeededForLeas: bool
    provideDigitalLearningContentForLeas: bool
    areOtherConditionsForLeas: bool
    otherConditionsForLeas: str
    wereAnyConditionsPlacedByStateForIheFunds: bool
    isStateIheGeerAwardConditionChanges: bool
    stateIheGeerAwardConditionChanges: str
    didStatePlaceDistanceLearningConditionsOnIhes: bool
    isSupportTechInfrastructureForIheDistanceLearning: bool
    isInternetAccessNeededForIhes: bool
    areDevicesNeededForIhes: bool
    isTrainingStaffNeededForIhes: bool
    provideDigitalLearningContentForIhes: bool
    areOtherConditionsForIhes: bool
    otherConditionsForIhes:str
    didStateDirectAnyIhesToUseGeerFundsForEmergency: bool
    numberOfPublicSchoolsReceivedGeerFunds: int
    numberOfNonPublicSchoolsReceivedGeerFunds: int

@dataclass
class GEER_Subgrantee:
    stateCode: str
    pk: str
    sk: str
    leaName: str
    iheName: str
    entityName: str
    dunsNumber: str
    awardedAmount: float
    awardedAmount_FLAG: str
    servedPopulation: str
    servedPopulation_FLAG: str
    fundsExpendedOnPublicSchools: float
    fundsExpendedOnPublicSchools_FLAG: str
    fundsExpendedOnNonPublicSchools: float
    fundsExpendedOnNonPublicSchools_FLAG: str
    fundsExpendedTotal: float
    fundsExpendedTotal_FLAG: str
    usedFundsForEducationalTechnology: bool
    usedFundsForEducationalTechnology_FLAG: str
    usedFundsToAssistDisadvantaged: bool
    usedFundsToAssistDisadvantaged_FLAG: str
    usedFundsForMentalHealth: bool
    usedFundsForMentalHealth_FLAG: str
    usedFundsForSanitization: bool
    usedFundsForSanitization_FLAG: str
    usedFundsForSummerAndAfterSchool: bool
    usedFundsForSummerAndAfterSchool_FLAG: str
    usedFundsForOther: bool
    usedFundsForOther_FLAG: str
    fundsUsedForOtherDescription: str
    fundsUsedForOtherDescription_FLAG: str
    usedFundsToProvideInternet: bool
    usedFundsToProvideInternet_FLAG: str
    usedFundsForMobileHotspots: bool
    usedFundsForMobileHotspots_FLAG: str
    usedFundsForInternetDevices: bool
    usedFundsForInternetDevices_FLAG:str
    usedFundsForHomeInternet: bool
    usedFundsForHomeInternet_FLAG: str
    usedFundsForDistrictInternet: bool
    usedFundsForDistrictInternet_FLAG: str
    usedFundsForOtherInternet: bool
    usedFundsForOtherInternet_FLAG: str
    usedFundsForOtherInternetDescription: str
    usedFundsForOtherInternetDescription_FLAG: str
    usedFundsForDedicatedLearningDevices: bool
    usedFundsForDedicatedLearningDevices_FLAG: str
    elementaryStudentsWithDedicatedDevice: int
    elementaryStudentsWithDedicatedDevice_FLAG: str
    elementaryStudentsEnrolled: int
    elementaryStudentsEnrolled_FLAG: str
    elementaryStudentProportionWithDevices: float
    elementaryStudentProportionWithDevices_FLAG: str
    elementaryStudentProportionWithDevices_calc: float
    elementaryStudentProportionWithDevices_calc_FLAG: str
    secondaryStudentsWithDedicatedDevice: int
    secondaryStudentsWithDedicatedDevice_FLAG: str
    secondaryStudentsEnrolled: int
    secondaryStudentsEnrolled_FLAG: str
    secondaryStudentProportionWithDevices: float
    secondaryStudentProportionWithDevices_FLAG: str
    secondaryStudentProportionWithDevices_calc: float
    secondaryStudentProportionWithDevices_calc_FLAG: str
    fundsExpendedByIhe: float
    fundsExpendedByIhe_FLAG: str
    fundsUsedToProvideFinancialAid: float
    fundsUsedToProvideFinancialAid_FLAG: str
    numberOfStudentsReceivedFinancialAid: int
    numberOfStudentsReceivedFinancialAid_FLAG: str
    fundsExpendedByEntity: float
    fundsExpendedByEntity_FLAG: str
    isPreKServed: bool
    isPreKServed_FLAG: str
    isK12Served: bool
    isK12Served_FLAG: str
    isPostSecServed: bool
    isPostSecServed_FLAG: str
    isDistanceLearningSupported: bool
    isDistanceLearningSupported_FLAG: str
    isDirectFinancialSupportProvided: bool
    isDirectFinancialSupportProvided_FLAG: str
    ftePositionsAsOf09302018: float
    ftePositionsAsOf09302018_FLAG: str
    ftePositionsAsOf09302019: float
    ftePositionsAsOf09302019_FLAG: str
    ftePositionsAsOf03132020: float
    ftePositionsAsOf03132020_FLAG: str
    ftePositionsAsOf09302020: float
    ftePositionsAsOf09302020_FLAG: str



class GEER_APR:
    styles = getSampleStyleSheet()
    styles.add(styles["Normal"].clone("Centered",alignment=TA_CENTER))
    styles.add(styles["Normal"].clone("Right",alignment=TA_RIGHT))
    styles.add(styles["Normal"].clone("BL1",bulletIndent=0.125 * inch))
    styles.add(styles["Normal"].clone("BL2",bulletIndent=0.25 * inch))
    styles.add(styles["Normal"].clone("BL3",bulletIndent=0.375 * inch))
    styles.add(styles["Normal"].clone("BL4",bulletIndent=0.5*inch))
    styles.add(styles["Normal"].clone("BL5",bulletIndent=0.625*inch))

    def __init__(self, version=1):
        self.width, self.height = letter
        self.version = version

    @staticmethod
    def _header_footer(canvas, document):
        # Save canvas state before drawing header and footer
        canvas.saveState()
        pageHeight=document.height+document.topMargin+document.bottomMargin
        canvas.setFont('Times-Bold',12)
        canvas.drawCentredString(document.width/2,
                                 pageHeight-0.4*inch,
                                 "CONTROLLED UNCLASSIFIED INFORMATION")
        canvas.setFont('Times-Roman',12)
        canvas.drawString(document.leftMargin,
                          pageHeight-0.6*inch,
                          "Conducted by: U.S. Department of Education")
        canvas.drawRightString(document.width,
                               pageHeight-0.6*inch,
                               "OMB No. 1810-0748 Expires 12/31/2023")
        canvas.drawCentredString(document.width/2,
                           0.4*inch,
                          f"Page {document.page}")
        if document.page == 1:
            canvas.drawString(document.leftMargin,
                              0.8*inch,
                              "Sensitive in Accordance with 32 CFR 2002")
            canvas.drawString(document.leftMargin,
                              0.6*inch,
                              ("Controlled by: Department of Education, "+
                               "Office of the Chief Data Officer, "+
                               f"{ISO}"))

        canvas.restoreState()

    def generate_subaward_content(self, subs: List[GEER_Subgrantee]) -> list:
        leaFlowables = []
        lineText=("4. For each LEA awarded GEER funds from the State, "+
                    "provide the amounts expended and select "+
                    "the purposes for which the funds were expended by the "+
                    "LEA. (If the SEA operates as a unitary system then report "+
                    "for the entire SEA.)")
        line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
        leaFlowables.append(line)

        iheFlowables = []
        lineText=("5. For each IHE awarded GEER funds from "+
                    "the State, provide the amount expended and additional "+ 
                    "information if GEER funds were used by the IHE to provide "+
                    "financial aid to students at the IHE.")
        line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
        iheFlowables.append(line)

        entityFlowables = []
        lineText=("6. What was the amount awarded and expended by each "+
                    "education-related entity? Which populations of students were"+
                    " or will be served by the entity? Did the funding awarded to "+
                    "the entity support distance-learning and remote education or "+
                    "provide financial support to students?")
        line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
        entityFlowables.append(line)

        fteFlowables = []
        lineText = "7. Provide the number of full-time equivalent (FTE) positions for the LEA, IHE, or Entity as of the listed reporting dates. (The number of FTE positions includes all staff regardless of whether the position is funded by Federal, State, local, or other funds —including instructional and non-instructional staff and contractors—and equals the sum of the number of full-time positions plus the full-time equivalent of the number of part-time positions.)"
        line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
        fteFlowables.append(line)
        heading1=Paragraph("<b>LEA Name/IHE/Entity Name</b>", style=GEER_APR.styles["Normal"])
        heading2=Paragraph("<b>DUNS number</b>", style=GEER_APR.styles["Normal"])
        heading3=Paragraph("<b>Full-time equivalent (FTE) positions as of September 30, 2018</b>", style=GEER_APR.styles["Normal"])
        heading4=Paragraph("<b>Full-time equivalent (FTE) positions as of September 30, 2019</b>", style=GEER_APR.styles["Normal"])
        heading5=Paragraph("<b>Full-time equivalent (FTE) positions as of March 13, 2020</b>", style=GEER_APR.styles["Normal"])
        heading6=Paragraph("<b>Full-time equivalent (FTE) positions on September 30, 2020</b>", style=GEER_APR.styles["Normal"])
        fteValues = [[heading1,heading2,heading3,heading4,heading5,heading6]]

        for sub in subs:
            if sub.leaName:
                lineText=f"<b>LEA:</b> {sub.leaName}"
                line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
                table = Table([[line]],
                              spaceBefore=9,
                              style=[('BACKGROUND',(0,0),(-1,0),(0.85,0.85,0.85)),
                                     ('GRID',(0,0),(-1,-1),0.25,(0,0,0))])
                leaFlowables.append(table)
                lineText=f"<b>DUNS #:</b> {sub.dunsNumber}"
                line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
                leaFlowables.append(line)
                heading1 = Paragraph("<b>Total amount awarded to the LEA</b>",style=GEER_APR.styles["Normal"])
                heading2 = Paragraph("<b>Amount expended by the LEA for Public Schools:</b>",style=GEER_APR.styles["Normal"])
                heading3 = Paragraph("<b>Amount expended by the LEA for equitable services for Non-public School students and teachers</b>",style=GEER_APR.styles["Normal"])
                heading4 = Paragraph("<b>Total amount expended by the LEA:</b>",style=GEER_APR.styles["Normal"])
                tableContent = [[heading1,heading2,heading3, heading4],
                                [f"${sub.awardedAmount:,.2f}" if sub.awardedAmount else '', 
                                f"${sub.fundsExpendedOnPublicSchools:,.2f}" if sub.fundsExpendedOnPublicSchools else '', 
                                f"${sub.fundsExpendedOnNonPublicSchools:,.2f}" if sub.fundsExpendedOnNonPublicSchools else '',
                                f"${sub.fundsExpendedTotal:,.2f}" if sub.fundsExpendedTotal else '']]
                table = Table(tableContent,
                              spaceBefore=6,
                              spaceAfter=6,
                              style=[('ALIGN',(0,0),(-1,0),'CENTER'),
                                    ('BACKGROUND',(0,0),(-1,0),(0.75,0.75,0.75)),
                                    ('GRID',(0,0),(-1,-1),0.25,(0,0,0))])
                leaFlowables.append(table)
                lineText=f"<b>Who is the LEA serving with these funds?:</b> {sub.servedPopulation}"
                line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
                leaFlowables.append(line)
                lineText="<b>Uses of GEER funds:</b>"
                line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
                leaFlowables.append(line)
                if sub.usedFundsForEducationalTechnology:
                    lineText=("<bullet>1.</bullet><b>Purchasing educational technology</b> "+
                    "(including hardware, software, and connectivity), which "+
                    "may include assistive technology or adaptive equipment. ")
                    line=Paragraph(lineText, style=GEER_APR.styles["BL1"])
                    leaFlowables.append(line)
                    if sub.usedFundsToProvideInternet:
                        lineText="<bullet>b.</bullet>Did this LEA use GEER funds to provide home Internet access for any students? Y"
                        line=Paragraph(lineText, style=GEER_APR.styles["BL2"])
                        leaFlowables.append(line)
                        lineText="If yes, what types of home Internet services were provided by the district using GEER funds?"
                        line=Paragraph(lineText, style=GEER_APR.styles["BL2"])
                        leaFlowables.append(line)
                        if sub.usedFundsForMobileHotspots:
                            lineText="<bullet>&bull;</bullet>Mobile hotspots with paid data plans"
                            line=Paragraph(lineText, style=GEER_APR.styles["BL3"])
                            leaFlowables.append(line)
                        if sub.usedFundsForInternetDevices:
                            lineText="<bullet>&bull;</bullet>Internet connected devices with paid data plans"
                            line=Paragraph(lineText, style=GEER_APR.styles["BL3"])
                            leaFlowables.append(line)
                        if sub.usedFundsForHomeInternet:
                            lineText="<bullet>&bull;</bullet>District pays for the cost of home Internet subscription for student"
                            line=Paragraph(lineText, style=GEER_APR.styles["BL3"])
                            leaFlowables.append(line)
                        if sub.usedFundsForDistrictInternet:
                            lineText="<bullet>&bull;</bullet>District provides home Internet access through a district-managed wireless network"
                            line=Paragraph(lineText, style=GEER_APR.styles["BL3"])
                            leaFlowables.append(line)
                        if sub.usedFundsForOtherInternet:
                            lineText=f"<bullet>&bull;</bullet>Other; If yes, please specify: {sub.usedFundsForOtherInternetDescription}"
                            line=Paragraph(lineText, style=GEER_APR.styles["BL3"])
                            leaFlowables.append(line)
                        lineText="<bullet>c.</bullet>Among students enrolled on September 30, 2020, what proportion of students by district had a dedicated LEA-provided device funded by GEER for the following grade bands? For the purposes of this survey, include desktop, laptop, and tablet computers (including Chromebooks and iPads). Do not include smartphone devices. “Elementary” is defined as “a school classified as elementary by state and local practice and composed of any span of grades not above grade 8” and “Secondary” is defined as “a school comprising any span of grades beginning with the next grade following an elementary or middle school (usually 7, 8, or 9) and ending with or below grade 12. Both junior high schools and senior high schools are included."
                        line=Paragraph(lineText, style=GEER_APR.styles["BL2"])
                        leaFlowables.append(line)
                        tableContent=[["Grade level",
                                       "Students with dedicated device provided by the LEA (Numerator)",
                                       "Students enrolled on September 30, 2020 (Denominator)",
                                       "Proportion of students with an LEA-provided device"],
                                      ["Elementary",f"{sub.elementaryStudentsWithDedicatedDevice}",f"{sub.elementaryStudentsEnrolled}",f"{sub.elementaryStudentProportionWithDevices}"],
                                      ["Secondary",f"{sub.secondaryStudentsWithDedicatedDevice}",f"{sub.secondaryStudentsEnrolled}",f"{sub.secondaryStudentProportionWithDevices}"]]
                        table = Table(tableContent,
                              spaceBefore=6,
                              spaceAfter=6,
                              style=[('ALIGN',(0,0),(-1,0),'CENTER'),
                                    ('BACKGROUND',(0,0),(-1,0),(0.75,0.75,0.75)),
                                    ('GRID',(0,0),(-1,-1),0.25,(0,0,0))])
                    else:
                        lineText="<bullet>b.</bullet>Did this LEA use GEER funds to provide home Internet access for any students? N"
                        line=Paragraph(lineText, style=GEER_APR.styles["BL2"])
                        leaFlowables.append(line)
                    
                if sub.usedFundsToAssistDisadvantaged:
                    lineText=("<bullet>2.</bullet>Activities focused specifically to "+
                                 "addressing the unique needs of low-income "+
                                 "children or students, children with "+
                                 "disabilities, English learners, racial and "+
                                 "ethnic minorities, students experiencing "+
                                 "homelessness, and foster care youth. ")
                    line=Paragraph(lineText, style=GEER_APR.styles["BL1"])
                    leaFlowables.append(line)
                if sub.usedFundsForMentalHealth:
                    lineText=("<bullet>3.</bullet>Providing mental health services and "+
                                 "supports. ")
                    line=Paragraph(lineText, style=GEER_APR.styles["BL1"])
                    leaFlowables.append(line)
                if sub.usedFundsForSanitization:
                    lineText=("<bullet>4.</bullet>Sanitization and minimizing the spread "+
                                 "of infectious diseases, including cleaning "+
                                 "supplies and staff training to address "+
                                 "sanitization and minimizing the spread of "+
                                 "infectious diseases. ")
                    line=Paragraph(lineText, style=GEER_APR.styles["BL1"])
                    leaFlowables.append(line)
                if sub.usedFundsForSummerAndAfterSchool:
                    lineText=("<bullet>5.</bullet>Summer learning and supplemental "+
                                 "afterschool programs. ")
                    line=Paragraph(lineText, style=GEER_APR.styles["BL1"])
                    leaFlowables.append(line)
                if sub.usedFundsForOther:
                    lineText=("<bullet>6.</bullet>Other (uses of funds not included above)."+
                                 f" If yes, please describe:{sub.fundsUsedForOtherDescription}")
                    line=Paragraph(lineText, style=GEER_APR.styles["BL1"])
                    leaFlowables.append(line)
                fteValues.append([sub.leaName,sub.dunsNumber,sub.ftePositionsAsOf09302018,sub.ftePositionsAsOf09302019,sub.ftePositionsAsOf03132020,sub.ftePositionsAsOf09302020])
            if sub.iheName:
                lineText=f"<b>IHE Name:</b> {sub.iheName}"
                line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
                table = Table([[line]],
                              spaceBefore=9,
                              style=[('BACKGROUND',(0,0),(-1,0),(0.85,0.85,0.85)),
                                     ('GRID',(0,0),(-1,-1),0.25,(0,0,0))])
                iheFlowables.append(table)
                lineText=f"<b>DUNS #:</b> {sub.dunsNumber}"
                line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
                iheFlowables.append(line)
                heading1 = Paragraph("<b>Amount awarded to the IHE</b>",style=GEER_APR.styles["Normal"])
                heading2 = Paragraph("<b>Amount expended by the IHE</b>",style=GEER_APR.styles["Normal"])
                heading3 = Paragraph("<b>Amount of expended funds used by the IHE to provide student financial aid grants</b>",style=GEER_APR.styles["Normal"])
                heading4 = Paragraph("<b>Number students who received financial aid grants as result of GEER funds</b>",style=GEER_APR.styles["Normal"])
                tableContent = [[heading1,heading2,heading3, heading4],
                                [f"${sub.awardedAmount:,.2f}" if sub.awardedAmount else '', 
                                f"${sub.fundsExpendedByIhe:,.2f}" if sub.fundsExpendedByIhe else '', 
                                f"${sub.fundsUsedToProvideFinancialAid:,.2f}" if sub.fundsUsedToProvideFinancialAid else '',
                                f"${sub.numberOfStudentsReceivedFinancialAid:,.2f}" if sub.numberOfStudentsReceivedFinancialAid else '']]
                table = Table(tableContent,
                              spaceBefore=6,
                              spaceAfter=6,
                              style=[('ALIGN',(0,0),(-1,0),'CENTER'),
                                    ('BACKGROUND',(0,0),(-1,0),(0.75,0.75,0.75)),
                                    ('GRID',(0,0),(-1,-1),0.25,(0,0,0))])
                iheFlowables.append(table)
                fteValues.append([sub.iheName,sub.dunsNumber,sub.ftePositionsAsOf09302018,sub.ftePositionsAsOf09302019,sub.ftePositionsAsOf03132020,sub.ftePositionsAsOf09302020])
            if sub.entityName:
                lineText=f"<b>Other Education-Related Entity:</b> {sub.entityName}"
                line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
                table = Table([[line]],
                              spaceBefore=9,
                              style=[('BACKGROUND',(0,0),(-1,0),(0.85,0.85,0.85)),
                                     ('GRID',(0,0),(-1,-1),0.25,(0,0,0))])
                entityFlowables.append(table)
                lineText=f"<b>DUNS #:</b> {sub.dunsNumber}"
                line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
                entityFlowables.append(line)
                heading1 = Paragraph("<b>Amount awarded to Entity</b>",style=GEER_APR.styles["Normal"])
                heading2 = Paragraph("<b>Amount expended by the Entity</b>",style=GEER_APR.styles["Normal"])
                heading3 = Paragraph("<b>Served Pre-K</b>",style=GEER_APR.styles["Normal"])
                heading4 = Paragraph("<b>Served K-12</b>",style=GEER_APR.styles["Normal"])
                heading4 = Paragraph("<b>Served Post-Sec</b>",style=GEER_APR.styles["Normal"])
                heading5 = Paragraph("<b>Supporting distance-learning and remote education</b>",style=GEER_APR.styles["Normal"])
                heading6 = Paragraph("<b>Direct financial support of students (e.g. scholarships)</b>",style=GEER_APR.styles["Normal"])
                isPreK = 'Y' if sub.isPreKServed else 'N'
                isK12 = 'Y' if sub.isK12Served else 'N'
                isPost = 'Y' if sub.isPostSecServed else 'N'
                isDist = 'Y' if sub.isDistanceLearningSupported else 'N'
                isDirect = 'Y' if sub.isDirectFinancialSupportProvided else 'N'
                tableContent = [[heading1,heading2,heading3, heading4, heading5, heading6],
                                [f"${sub.awardedAmount:,.2f}" if sub.awardedAmount else '', 
                                f"${sub.fundsExpendedByEntity:,.2f}" if sub.fundsExpendedByEntity else '', 
                                isPreK, isK12, isPost, isDist, isDirect]]
                table = Table(tableContent,
                              spaceBefore=6,
                              spaceAfter=6,
                              style=[('ALIGN',(0,0),(-1,0),'CENTER'),
                                    ('BACKGROUND',(0,0),(-1,0),(0.75,0.75,0.75)),
                                    ('GRID',(0,0),(-1,-1),0.25,(0,0,0))])
                entityFlowables.append(table)
                fteValues.append([sub.entityName,sub.dunsNumber,sub.ftePositionsAsOf09302018,sub.ftePositionsAsOf09302019,sub.ftePositionsAsOf03132020,sub.ftePositionsAsOf09302020])
                table = Table(fteValues,
                              spaceBefore=9,
                              spaceAfter=6,
                              style=[('ALIGN',(0,0),(-1,0),'CENTER'),
                                    ('BACKGROUND',(0,0),(-1,0),(0.75,0.75,0.75)),
                                    ('GRID',(0,0),(-1,-1),0.25,(0,0,0))])
                fteFlowables.append(table)

        return leaFlowables+iheFlowables+entityFlowables+fteFlowables

                

    def generate(self, row: GEER_Grantee, subs: List[GEER_Subgrantee]):
        # Name the PDF after the grantee and grant PR Number
        pdfName = row.stateCode + '-' + row.prNumber + ".pdf"
        pdf = SimpleDocTemplate(pdfName,
                                pagesize=letter,
                                rightMargin=36,
                                leftMargin=36,
                                topMargin=72,
                                bottomMargin=72)

        flowables = []

        introText = ("Education Stabilization Fund--Governor's Emergency "+
                     "Education Relief Fund")
        introParagraph = Paragraph(introText, style=GEER_APR.styles["Title"])
        flowables.append(introParagraph)

        introText = "(GEER Fund) Recipient Reporting Data Collection Form"
        introParagraph = Paragraph(introText, style=GEER_APR.styles["Title"])
        flowables.append(introParagraph)

        introText = "Final Version: December 2020"
        oos = GEER_APR.styles["Centered"]
        oos.spaceAfter=9
        introParagraph = Paragraph(introText,style=oos)
        flowables.append(introParagraph)

        headingText="GEER Fund Reporting Form"
        heading=Paragraph(headingText, style=GEER_APR.styles["Heading1"])
        flowables.append(heading)

        lineText=f"State: {row.stateCode}"
        line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
        flowables.append(line)      

        lineText=f"PR/Award number: {row.prNumber}"
        line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
        flowables.append(line)

        lineText=f"State Director: {row.repName}"
        line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
        flowables.append(line)

        lineText=f"Position: {row.repPosition}"
        line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
        flowables.append(line)

        lineText=f"Office: {row.repOffice}"
        line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
        flowables.append(line)

        lineText=f"Telephone: {row.repPhone}"
        line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
        flowables.append(line)

        lineText=f"E-mail Address: {row.repEmail}"
        line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
        flowables.append(line)

        lineText=("<b>Instructions:</b> States and outlying areas that "+
                  "received Governors Emergency Education Relief (GEER) or "+
                  "Education Stabilization Fund (ESF)-Governors funds should "+
                  "fill out this form. References to GEER include "+
                  "ESF-Governors. To fulfill the annual GEER fund reporting "+
                  "requirements, answer all questions based on the reporting "+
                  "period shown in the Annual Reporting table below.")
        oos = GEER_APR.styles["Normal"]
        oos.spaceBefore=9
        line=Paragraph(lineText, style=oos)
        flowables.append(line)

        lineText=("<b>Annual Reporting: This report should be completed based "+
                  "on activities in the applicable reporting periods.</b>")
        line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
        flowables.append(line)

        reportingPeriods = [["Annual Report",
                             "Due Date",
                             "Applicable Reporting Period"],
                            ["First Annual Report",
                             "February 1, 2021",
                             "March 13, 2020 - September 20, 2020"],
                            ["Second Annual Report",
                             "February 1, 2022",
                             "October 1, 2020 - September 30, 2021"],
                            ["Third Annual Report",
                             "February 1, 2023",
                             "October 1, 2021 - September 30, 2022"]]
        table = Table(reportingPeriods,
                      spaceBefore=18,
                      spaceAfter=18,
                      style=[('ALIGN',(0,0),(-1,0),'CENTER'),
                            ('BACKGROUND',(0,0),(-1,0),(0.75,0.75,0.75)),
                            ('GRID',(0,0),(-1,-1),0.25,(0,0,0))])
        flowables.append(table)

        lineText = ("The total grant amount allocated to the State is "+
                   f"${row.grantAmountAllocated:,.2f}" if row.grantAmountAllocated else '')
        line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
        flowables.append(line)
        
        lineText = ("The total amount of the grant expended is "+
                    f"${row.grantAmountExpended:,.2f}" if row.grantAmountExpended else '')
        line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
        flowables.append(line)
        
        lineText = ("1. Which types of entities within the State were awarded "+
                   "Governors Emergency Education Relief (GEER) funds?")
        oos=GEER_APR.styles["Normal"]
        oos.spaceBefore=9
        line=Paragraph(lineText, style=oos)
        flowables.append(line)

        answer = 'Y' if row.areLeasAwardedGeerFunds else 'N'
        lineText = ("<bullet>&bull;</bullet>Local Educational Agencies (LEAs) "+
                   f"{answer}")
        line=Paragraph(lineText, style=GEER_APR.styles["BL1"])
        flowables.append(line)

        answer = 'Y' if row.areIhesAwardedGeerFunds else 'N'
        lineText = ("<bullet>&bull;</bullet>Institutions of Higher Education "+
                   f"(IHEs) {answer}")
        line=Paragraph(lineText, style=GEER_APR.styles["BL1"])
        flowables.append(line)

        answer = 'Y' if row.areEntitiesAwardedGeerFunds else 'N'
        lineText = ("<bullet>&bull;</bullet>Other Education-Related Entities "+
                   f"{answer}")
        line=Paragraph(lineText, style=GEER_APR.styles["BL1"])
        flowables.append(line)
        
        if row.wereAnyConditionsPlacedByStateForLeaFunds:
            lineText = ("2. Did the State place any funding conditions or "+
                       "requirements on GEER awards for LEAs to ensure that "+
                       "the funds were spent on specific purposes or "+
                       "activities? Y")
            line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
            flowables.append(line)

            if row.isStateLeaGeerAwardConditionChanges:
                lineText = ("<bullet>a.</bullet>Were there any changes to the"+
               "State’s LEA GEER award conditions or requirements since the "+
               "State’s initial 45-day report to the Department of Education? "+
               f"Y  If yes, please specify changes: {row.stateLeaGeerAwardConditionChanges}")
            else:
                lineText = ("<bullet>a.</bullet>Were there any changes to the"+
                           "State’s LEA GEER award conditions or requirements "+
                           "since the State’s initial 45-day report to the "+
                           "Department of Education? N")
            line=Paragraph(lineText, style=GEER_APR.styles["BL2"])
            flowables.append(line)
            if row.didStatePlaceDistanceLearningConditionsOnLeas:
                lineText=("<bullet>b.</bullet>Did the State place any funding "+
                          "conditions or requirements directing LEAs to use "+
                          "the funds for activities related to "+
                          "distance-learning and remote education? Y")
                line=Paragraph(lineText, style=GEER_APR.styles["BL2"])
                flowables.append(line)
                lineText=("<bullet>ii.</bullet>If yes, what were the "+
                          "directed activities?")
                line=Paragraph(lineText, style=GEER_APR.styles["BL3"])
                flowables.append(line)
                if row.isSupportTechInfrastructureForIheDistanceLearning:
                    lineText=("<bullet>&bull;</bullet>Support access to the "+
                              "technology infrastructure required for distance"+
                              "education: Y. If yes,")
                    line=Paragraph(lineText, style=GEER_APR.styles["BL4"])
                    flowables.append(line)
                    answer='Y' if row.isInternetAccessNeededForLeas else 'N'
                    lineText=("<bullet>&bull;</bullet>For Internet Access: "+
                              f"{answer}")
                    line=Paragraph(lineText, style=GEER_APR.styles["BL5"])
                    flowables.append(line)
                    answer='Y' if row.areDevicesNeededForLeas else 'N'
                    lineText=f"<bullet>&bull;</bullet>For Devices: {answer}"
                    line=Paragraph(lineText, style=GEER_APR.styles["BL5"])
                    flowables.append(line)
                else:
                    lineText=("<bullet>&bull;</bullet>Support access to the "+
                              "technology infrastructure required for distance"+
                              "education: N.")
                    line=Paragraph(lineText, style=GEER_APR.styles["BL4"])
                    flowables.append(line)
                answer='Y' if row.isTrainingStaffNeededForLeas else 'N'
                lineText=("<bullet>&bull;</bullet>Training staff/faculty for "+
                          f"distance-learning and remote education: {answer}")
                line=Paragraph(lineText, style=GEER_APR.styles["BL4"])
                flowables.append(line)
                answer='Y' if row.provideDigitalLearningContentForLeas else 'N'
                lineText=("<bullet>&bull;</bullet>Providing digital learning "+
                          f"content, applications, and tools: {answer}")
                line=Paragraph(lineText, style=GEER_APR.styles["BL4"])
                flowables.append(line)

                if row.areOtherConditionsForLeas:
                    lineText=("Other: Y. If yes, please specify: "+
                              f"{row.otherConditionsForLeas}")
                else:
                    lineText="Other: N."
                line=Paragraph(lineText, style=GEER_APR.styles["BL4"])
                flowables.append(line)
            else:
                lineText=("<bullet>b.</bullet>Did the State place any funding"+
                          "conditions or requirements directing LEAs to use the"+
                          "funds for activities related to distance-learning "+
                          "and remote education? N")
                line=Paragraph(lineText, style=GEER_APR.styles["BL2"])
                flowables.append(line)
        else:
            lineText = ("2. Did the State place any funding conditions or "+
                        "requirements on GEER awards for LEAs to ensure that"+
                        "the funds were spent on specific purposes or "+
                        "activities? N")
            line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
            flowables.append(line)

        if row.wereAnyConditionsPlacedByStateForIheFunds:
            lineText=("3. Did the State place any funding conditions or "+
                      "requirements on GEER awards for IHEs to ensure that "+
                      "the funds were spent on specific purposes or "+
                      "activities? Y If yes,")
            line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
            flowables.append(line)
            if row.isStateIheGeerAwardConditionChanges:
                lineText=("<bullet>a.</bullet>Were there any changes to the "+
                          "State’s IHE GEER award conditions or requirements "+
                          "since the State’s initial 45-day report to the "+
                          "Department of Education? Y If yes, please specify "+
                          f"the changes: {row.stateIheGeerAwardConditionChanges}")
            else:
                lineText=("<bullet>a.</bullet>Were there any changes to the "+
                          "State’s IHE GEER award conditions or requirements "+
                          "since the State’s initial 45-day report to the "+
                          "Department of Education? N")
            line=Paragraph(lineText, style=GEER_APR.styles["BL1"])
            flowables.append(line)
            if row.didStatePlaceDistanceLearningConditionsOnIhes:
                lineText=("<bullet>b.</bullet>Did the State place any funding "+
                          "conditions or requirements directing IHEs to use "+
                          "the funds for activities related to "+
                          "distance-learning and remote education? Y")
                line=Paragraph(lineText, style=GEER_APR.styles["BL1"])
                flowables.append(line)
                lineText=("<bullet>ii.</bullet>If yes, what were the directed "+
                          "activities?")
                line=Paragraph(lineText, style=GEER_APR.styles["BL2"])
                flowables.append(line)
                if row.isSupportTechInfrastructureForIheDistanceLearning:
                    lineText=("<bullet>&bull;</bullet>Support access to the "+
                              "technology infrastructure required for distance"+
                              "education: Y. If yes,")
                    line=Paragraph(lineText, style=GEER_APR.styles["BL3"])
                    flowables.append(line)
                    answer='Y' if row.isInternetAccessNeededForIhes else 'N'
                    lineText=("<bullet>&bull;</bullet>For Internet Access: "+
                              f"{answer}")
                    line=Paragraph(lineText, style=GEER_APR.styles["BL4"])
                    flowables.append(line)
                    answer='Y' if row.areDevicesNeededForIhes else 'N'
                    lineText=f"<bullet>&bull;</bullet>For Devices: {answer}"
                    line=Paragraph(lineText, style=GEER_APR.styles["BL4"])
                    flowables.append(line)
                else:
                    lineText=("<bullet>&bull;</bullet>Support access to the "+
                              "technology infrastructure required for "+
                              "distance education: N.")
                    line=Paragraph(lineText, style=GEER_APR.styles["BL3"])
                    flowables.append(line)
                answer='Y' if row.isTrainingStaffNeededForIhes else 'N'
                lineText=("<bullet>&bull;</bullet>Training staff/faculty for"+
                          f"distance-learning and remote education: {answer}")
                line=Paragraph(lineText, style=GEER_APR.styles["BL3"])
                flowables.append(line)
                answer='Y' if row.provideDigitalLearningContentForIhes else 'N'
                lineText=("<bullet>&bull;</bullet>Providing digital learning "+
                          f"content, applications, and tools: {answer}")
                line=Paragraph(lineText, style=GEER_APR.styles["BL3"])
                flowables.append(line)
                if row.areOtherConditionsForIhes:
                    lineText=("<bullet>&bull;</bullet>Other: Y If yes, please "+
                              f"specify: {row.otherConditionsForIhes}")
                else:
                    lineText="<bullet>&bull;</bullet>Other: N"
                line=Paragraph(lineText, style=GEER_APR.styles["BL3"])
                flowables.append(line)
                answer='Y' if row.didStateDirectAnyIhesToUseGeerFundsForEmergency else 'N'
                lineText=("<bullet>c.</bullet>Did the State direct any IHEs "+
                          "to use GEER funds for emergency financial aid "+
                          f"grants to students? {answer}")
                line=Paragraph(lineText, style=GEER_APR.styles["BL3"])
                flowables.append(line)
            else:
                lineText=("<bullet>b.</bullet>Did the State place any funding "+
                          "conditions or requirements directing IHEs to use "+
                          "the funds for activities related to "+
                          "distance-learning and remote education? N")
                line=Paragraph(lineText, style=GEER_APR.styles["BL1"])
                flowables.append(line)
        else:
            lineText=("3. Did the State place any funding conditions or "+
                      "requirements on GEER awards for IHEs to ensure that "+
                      "the funds were spent on specific purposes or "+
                      "activities? N")
            line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
            flowables.append(line)

        # Insert Sub Grantees content here
        flowables.extend(self.generate_subaward_content(subs))

        lineText="8. In the table below, indicate the number of K-12 schools (public and non-public) that received GEER funds or received services paid for with GEER funds."
        line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
        flowables.append(line)
        heading1=Paragraph("<b>School Type</b>", style=GEER_APR.styles["Normal"])
        heading2=Paragraph("<b>K-12 schools</b>", style=GEER_APR.styles["Normal"])
        label1=Paragraph("<b>Public Schools</b>", style=GEER_APR.styles["Normal"])
        label2=Paragraph("<b>Non-public Schools</b>", style=GEER_APR.styles["Normal"])
        tableContent=[[heading1, heading2],
                      [label1,f"{row.numberOfPublicSchoolsReceivedGeerFunds}"],
                      [label2,f"{row.numberOfNonPublicSchoolsReceivedGeerFunds}"]]
        table = Table(tableContent,
                      spaceBefore=9,
                      spaceAfter=18,
                      style=[('ALIGN',(0,0),(-1,0),'CENTER'),
                            ('BACKGROUND',(0,0),(-1,0),(0.75,0.75,0.75)),
                            ('BACKGROUND',(0,1),(0,-1),(0.75,0.75,0.75)),
                            ('GRID',(0,0),(-1,-1),0.25,(0,0,0))])
        flowables.append(table)

        lineText="Burden Statement"
        oos=GEER_APR.styles["Heading1"]
        oos.spaceBefore=0.5*inch
        line=Paragraph(lineText, style=oos)
        flowables.append(line)
        lineText=("According to the Paperwork Reduction Act of 1995, no "+
                  "persons are required to respond to a collection of "+
                  "information unless such collection displays a valid OMB "+
                  "control number. The valid OMB control number for this "+
                  "information collection is 1810-0748. Public reporting "+
                  "burden for this collection of information is estimated "+
                  "to average 4.1 hours per response, including time for "+
                  "reviewing instructions, searching existing data sources, "+
                  "gathering and maintaining the data needed, and completing "+
                  "and reviewing the collection of information. Under the "+
                  "PRA, participants are required to respond to this "+
                  "collection to obtain or retain a benefit. If you have any "+
                  "comments concerning the accuracy of the time "+
                  "estimate, suggestions for improving this individual "+
                  "collection, or if you have comments or concerns regarding "+
                  "the status of your individual form, please contact Joanne "+
                  "Bogart, US. Department of Education, 400 Maryland Avenue, "+
                  "SW, Washington, DC 20202.")
        line=Paragraph(lineText, style=GEER_APR.styles["Normal"])
        flowables.append(line)

        logging.info('Building document')
        pdf.build(flowables,onFirstPage=self._header_footer,
                  onLaterPages=self._header_footer)

    

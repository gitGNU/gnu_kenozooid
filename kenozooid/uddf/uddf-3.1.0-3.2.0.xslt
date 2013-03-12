<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:uddf31="http://www.streit.cc/uddf/3.1/"
    xmlns="http://www.streit.cc/uddf/3.2/"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    exclude-result-prefixes="uddf31">

<!-- change namespace of all elements -->
<xsl:template match="uddf31:*">
    <xsl:element name="{local-name()}" namespace="http://www.streit.cc/uddf/3.2/">
        <xsl:apply-templates select="@* | node()"/>
    </xsl:element>
</xsl:template>

<xsl:template match="@xsi:schemaLocation">
    <xsl:attribute name="xsi:schemaLocation">http://www.streit.cc/uddf/3.2/</xsl:attribute>
</xsl:template>

<!-- copy all attributes -->
<xsl:template match="@*">
    <xsl:copy/>
</xsl:template>

<!-- update uddf version -->
<xsl:template match="uddf31:uddf/@version">
    <xsl:attribute name="version">3.2.0</xsl:attribute>
</xsl:template>

<!-- inject kenozooid specific information -->
<xsl:template match="uddf31:generator">
    <xsl:element name="{local-name()}" namespace="http://www.streit.cc/uddf/3.2/">
        <xsl:comment>Upgraded by Kenozooid 0.13.0.</xsl:comment>
        <xsl:apply-templates/>
    </xsl:element>
</xsl:template>

</xsl:stylesheet> 

<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:uddf30="http://www.streit.cc/uddf/3.0/"
    xmlns="http://www.streit.cc/uddf/3.1/"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    exclude-result-prefixes="uddf30">

<!-- change namespace of all elements -->
<xsl:template match="uddf30:*">
    <xsl:element name="{local-name()}" namespace="http://www.streit.cc/uddf/3.1/">
        <xsl:apply-templates select="@* | node()"/>
    </xsl:element>
</xsl:template>

<xsl:template match="@xsi:schemaLocation">
    <xsl:attribute name="xsi:schemaLocation">http://www.streit.cc/uddf/3.1/</xsl:attribute>
</xsl:template>

<!-- copy all attributes -->
<xsl:template match="@*">
    <xsl:copy/>
</xsl:template>

<!-- update uddf version -->
<xsl:template match="uddf30:uddf/@version">
    <xsl:attribute name="version">3.1.0</xsl:attribute>
</xsl:template>

<!-- copy dive computer name from dive computer model if name not specified -->
<xsl:template match="uddf30:divecomputer">
    <xsl:if test="not(name)">
        <divecomputer>
            <xsl:apply-templates select="@*"/>
            <name><xsl:value-of select="uddf30:model/text()"/></name>
            <xsl:apply-templates/>
        </divecomputer>
    </xsl:if>
</xsl:template>

<!-- set setpo2@setby attribute to user if not set -->
<xsl:template match="uddf30:setpo2">
    <xsl:if test="not(@setby)">
        <setpo2>
            <xsl:apply-templates select="@*"/>
            <xsl:attribute name="setby">user</xsl:attribute>
            <xsl:apply-templates/>
        </setpo2>
    </xsl:if>
</xsl:template>

<!-- inject kenozooid specific information -->
<xsl:template match="uddf30:generator">
    <xsl:element name="{local-name()}">
        <xsl:comment>Upgraded by Kenozooid 0.6.0.</xsl:comment>
        <xsl:apply-templates/>
    </xsl:element>
</xsl:template>

</xsl:stylesheet> 

<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0" 
 xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" 
 xmlns="http://www.opengis.net/sld" 
 xmlns:ogc="http://www.opengis.net/ogc" 
 xmlns:xlink="http://www.w3.org/1999/xlink" 
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <!-- a Named Layer is the basic building block of an SLD document -->
  <NamedLayer>
    <Name>default_point</Name>
    <UserStyle>
    <!-- Styles can have names, titles and abstracts -->
      <Title>radiosonde launch status</Title>
      <Abstract>radiosonde observation availability according to data in NWP centers</Abstract>
      <FeatureTypeStyle>
        <Rule>
         <Name>black</Name>
		   <ogc:Filter>
             <ogc:PropertyIsEqualTo>
               <ogc:PropertyName>sondestatus</ogc:PropertyName>
			   <ogc:Literal>empty</ogc:Literal>
             </ogc:PropertyIsEqualTo>
               </ogc:Filter>
           <PointSymbolizer>
			 <Graphic>
			   <Mark>
                 <WellKnownName>circle</WellKnownName>
                 <Fill><CssParameter name="fill">#000000</CssParameter></Fill>
			   </Mark>                         
               <Size>8</Size>
			 </Graphic>
		   </PointSymbolizer>
		</Rule>
	  
	  <Rule>
         <Name>green</Name>
		  <ogc:Filter>
             <ogc:PropertyIsEqualTo>
               <ogc:PropertyName>sondestatus</ogc:PropertyName>
			   <ogc:Literal>complete</ogc:Literal>
             </ogc:PropertyIsEqualTo>
               </ogc:Filter>
		   <PointSymbolizer>
			 <Graphic>
			   <Mark>
                 <WellKnownName>circle</WellKnownName>
				 <Fill><CssParameter name="fill">#009900</CssParameter></Fill>
               </Mark>
              <Size>8</Size>
			 </Graphic>
		   </PointSymbolizer>
		</Rule>
        
         <Rule>
         <Name>Pilot</Name>
		  <ogc:Filter>
             <ogc:PropertyIsEqualTo>
               <ogc:PropertyName>sondestatus</ogc:PropertyName>
			   <ogc:Literal>pilot</ogc:Literal>
             </ogc:PropertyIsEqualTo>
               </ogc:Filter>
		   <PointSymbolizer>
			 <Graphic>
			   <Mark>
                 <WellKnownName>circle</WellKnownName>
				 <Fill><CssParameter name="fill">#334CFF</CssParameter></Fill>
               </Mark>
              <Size>8</Size>
			 </Graphic>
		   </PointSymbolizer>
		</Rule>


        <Rule>
         <Name>yellow (incomplete variables)</Name>
		   <ogc:Filter>
             <ogc:PropertyIsEqualTo>
               <ogc:PropertyName>sondestatus</ogc:PropertyName>
			   <ogc:Literal>incompletevariables</ogc:Literal>
             </ogc:PropertyIsEqualTo>
               </ogc:Filter>
		   <PointSymbolizer>
			 <Graphic>
			   <Mark>
                 <WellKnownName>circle</WellKnownName>
				 <Fill><CssParameter name="fill">#FFFF00</CssParameter></Fill>
               </Mark>
              <Size>8</Size>
			 </Graphic>
		   </PointSymbolizer>
		</Rule>

        
         <Rule>
         <Name>yellow (incomplete layer)</Name>
		   <ogc:Filter>
             <ogc:PropertyIsEqualTo>
               <ogc:PropertyName>sondestatus</ogc:PropertyName>
			   <ogc:Literal>incompletelayers</ogc:Literal>
             </ogc:PropertyIsEqualTo>
               </ogc:Filter>
		   <PointSymbolizer>
			 <Graphic>
			   <Mark>
                 <WellKnownName>circle</WellKnownName>
				 <Fill><CssParameter name="fill">#FF8000</CssParameter></Fill>
               </Mark>
              <Size>8</Size>
			 </Graphic>
		   </PointSymbolizer>
		</Rule>

        <Rule>
         <Name>not in vola</Name>
		   <ogc:Filter>
             <ogc:PropertyIsEqualTo>
               <ogc:PropertyName>sondestatus</ogc:PropertyName>
			   <ogc:Literal>notinvola</ogc:Literal>
             </ogc:PropertyIsEqualTo>
               </ogc:Filter>
          <PointSymbolizer>
			 <Graphic>
			   <Mark>
                 <WellKnownName>circle</WellKnownName>
                 <Fill><CssParameter name="fill">#FF00BF</CssParameter></Fill>
                 <!--			     
                 <Stroke>
                    <CssParameter name="stroke">#0000FF</CssParameter>

                   <CssParameter name="stroke">#333333</CssParameter>
                   <CssParameter name="stroke-width">1</CssParameter>
                 </Stroke>
				-->
               </Mark>
               <Size>8</Size>
			 </Graphic>
		   </PointSymbolizer>
      	</Rule>       
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
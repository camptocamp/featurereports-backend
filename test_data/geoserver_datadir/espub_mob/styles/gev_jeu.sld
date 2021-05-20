<?xml version="1.0" encoding="UTF-8"?>
<!--
  
  nom du SLD : gev_jeu
  
  couche source dans la base :  espace_public.gev_jeu
  layer cible du style       :  espub_mob:gev_jeu
  
  objet :  style Geojardins des jeux des espaces verts de la Ville de Rennes
  
  Historique des versions :
  date        |  auteur              |  description
  17/02/2017  |  Maël REBOUX         |  version initiale
  21/07/2020  |  S GELIN             |  modif
  04/11/2020  |  Maël REBOUX         |  passage uom + 1/5000 max + styles pour les petites échelles
  
-->
<StyledLayerDescriptor version="1.1.0" xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" xmlns="http://www.opengis.net/sld" 
xmlns:ogc="http://www.opengis.net/ogc" xmlns:se="http://www.opengis.net/se" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NamedLayer>
    <se:Name>espub_mob:gev_jeu</se:Name>
    <UserStyle>
      <se:Name>gev_jeu</se:Name>
        <se:Description>
          <se:Title>Jeux des espaces verts de la Ville de Rennes</se:Title>
          <se:Abstract>style pour GéoJardins</se:Abstract>
        </se:Description>
      <se:FeatureTypeStyle>
        
        <!-- petites échelles : point blanc dans point de couleur -->
        <se:Rule>
          <se:MinScaleDenominator>1</se:MinScaleDenominator>
          <se:MaxScaleDenominator>100000</se:MaxScaleDenominator>
           <se:PointSymbolizer>
            <se:Graphic>
              <se:Mark>
                <se:WellKnownName>circle</se:WellKnownName>
                <se:Fill>
                  <se:SvgParameter name="fill">#ffaa00</se:SvgParameter>
                </se:Fill>
                </se:Mark>
              <se:Size>9</se:Size>
            </se:Graphic>
          </se:PointSymbolizer>
          <se:PointSymbolizer>
            <se:Graphic>
              <se:Mark>
                <se:WellKnownName>circle</se:WellKnownName>
                <se:Fill>
                  <se:SvgParameter name="fill">#ffffff</se:SvgParameter>
                </se:Fill>     
              </se:Mark>
              <se:Size>4</se:Size>
            </se:Graphic>
          </se:PointSymbolizer>
        </se:Rule>
        
      </se:FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
/* Carries the LUT theme's images and fonts into the rendered deck.
 *
 * The theme's backgrounds and logo overlays are referenced from the compiled
 * reveal.js theme CSS. An extension cannot otherwise get asset files into the
 * output tree — format-resources does not copy them — but Quarto copies a
 * reveal plugin directory wholesale, so the assets ride along inside one.
 *
 * The plugin does nothing at run time. It exists for its files.
 */
window.LutAssets = function () {
  return { id: 'lut-assets' };
};
